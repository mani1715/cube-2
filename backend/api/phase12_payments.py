"""
PHASE 12.1 - Payment Integration with Razorpay
Handles payment orders, verification, and transaction management
"""

import os
import uuid
import logging
import razorpay
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from pymongo import MongoClient
from api.phase12_email import send_email_async, create_payment_success_email

# Logger setup
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client[DB_NAME]

# Razorpay client
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Router
phase12_payments_router = APIRouter(prefix="/api/phase12/payments", tags=["Phase 12 - Payments"])

# Pydantic Models
class CreateOrderRequest(BaseModel):
    """Request to create a payment order"""
    amount: float = Field(..., description="Amount in INR (e.g., 499.00)")
    item_type: str = Field(..., description="Type: session, event, blog")
    item_id: str = Field(..., description="ID of the item being purchased")
    item_name: str = Field(..., description="Name/title of the item")
    user_email: Optional[str] = Field(None, description="User email for receipt")
    user_name: Optional[str] = Field(None, description="User name")
    user_phone: Optional[str] = Field(None, description="User phone")


class VerifyPaymentRequest(BaseModel):
    """Request to verify payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentStatusResponse(BaseModel):
    """Payment status response"""
    transaction_id: str
    status: str
    amount: float
    item_type: str
    item_id: str
    created_at: str


# ==================== PAYMENT ENDPOINTS ====================

@phase12_payments_router.post("/create-order")
async def create_payment_order(order_request: CreateOrderRequest):
    """
    Create a Razorpay order for payment
    Amount is converted from INR to paise (multiply by 100)
    """
    try:
        # Convert amount to paise (Razorpay requires amount in smallest currency unit)
        amount_paise = int(order_request.amount * 100)
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,  # Auto-capture payment
            "notes": {
                "item_type": order_request.item_type,
                "item_id": order_request.item_id,
                "item_name": order_request.item_name
            }
        })
        
        # Create transaction record in database
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": order_request.amount,
            "amount_paise": amount_paise,
            "currency": "INR",
            "item_type": order_request.item_type,
            "item_id": order_request.item_id,
            "item_name": order_request.item_name,
            "user_email": order_request.user_email,
            "user_name": order_request.user_name,
            "user_phone": order_request.user_phone,
            "status": "created",
            "payment_method": None,
            "razorpay_payment_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        db.transactions.insert_one(transaction)
        
        logger.info(f"Payment order created: {transaction_id} for {order_request.item_type} - {order_request.item_id}")
        
        return {
            "transaction_id": transaction_id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": order_request.amount,
            "currency": "INR",
            "razorpay_key_id": RAZORPAY_KEY_ID
        }
        
    except Exception as e:
        logger.error(f"Failed to create payment order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment order: {str(e)}")


@phase12_payments_router.post("/verify-payment")
async def verify_payment(verify_request: VerifyPaymentRequest, background_tasks: BackgroundTasks):
    """
    Verify Razorpay payment signature and update transaction status
    """
    try:
        # Verify signature
        params_dict = {
            "razorpay_order_id": verify_request.razorpay_order_id,
            "razorpay_payment_id": verify_request.razorpay_payment_id,
            "razorpay_signature": verify_request.razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Signature is valid - fetch payment details
        payment_details = razorpay_client.payment.fetch(verify_request.razorpay_payment_id)
        
        # Update transaction in database
        update_result = db.transactions.update_one(
            {"razorpay_order_id": verify_request.razorpay_order_id},
            {
                "$set": {
                    "status": "success",
                    "razorpay_payment_id": verify_request.razorpay_payment_id,
                    "payment_method": payment_details.get("method", "unknown"),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Fetch updated transaction
        transaction = db.transactions.find_one(
            {"razorpay_order_id": verify_request.razorpay_order_id},
            {"_id": 0}
        )
        
        logger.info(f"Payment verified successfully: {transaction['transaction_id']}")
        
        # Send payment success email in background
        if transaction.get("user_email"):
            background_tasks.add_task(
                send_payment_success_email_task,
                to_email=transaction["user_email"],
                user_name=transaction.get("user_name", "Customer"),
                transaction_id=transaction["transaction_id"],
                amount=transaction["amount"],
                item_name=transaction["item_name"],
                payment_method=transaction.get("payment_method", "N/A")
            )
        
        return {
            "success": True,
            "transaction_id": transaction["transaction_id"],
            "message": "Payment verified successfully"
        }
        
    except razorpay.errors.SignatureVerificationError:
        logger.error("Payment signature verification failed")
        
        # Mark transaction as failed
        db.transactions.update_one(
            {"razorpay_order_id": verify_request.razorpay_order_id},
            {
                "$set": {
                    "status": "failed",
                    "error": "Signature verification failed",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        raise HTTPException(status_code=400, detail="Payment signature verification failed")
        
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")


@phase12_payments_router.post("/webhook")
async def razorpay_webhook(request: Request):
    """
    Handle Razorpay webhooks for payment status updates
    """
    try:
        # Get request body and signature
        payload = await request.body()
        signature = request.headers.get("X-Razorpay-Signature", "")
        
        # Verify webhook signature
        razorpay_client.utility.verify_webhook_signature(
            payload.decode(),
            signature,
            RAZORPAY_WEBHOOK_SECRET
        )
        
        # Parse webhook data
        import json
        webhook_data = json.loads(payload.decode())
        
        event = webhook_data.get("event")
        payload_data = webhook_data.get("payload", {})
        payment = payload_data.get("payment", {}).get("entity", {})
        
        logger.info(f"Webhook received: {event}")
        
        # Update transaction based on event
        if event == "payment.captured":
            db.transactions.update_one(
                {"razorpay_payment_id": payment.get("id")},
                {
                    "$set": {
                        "status": "success",
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        elif event == "payment.failed":
            db.transactions.update_one(
                {"razorpay_order_id": payment.get("order_id")},
                {
                    "$set": {
                        "status": "failed",
                        "error": payment.get("error_description", "Payment failed"),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@phase12_payments_router.get("/transaction/{transaction_id}")
async def get_transaction_status(transaction_id: str):
    """
    Get transaction status by transaction ID
    """
    try:
        transaction = db.transactions.find_one(
            {"transaction_id": transaction_id},
            {"_id": 0}
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {
            "success": True,
            "transaction": transaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction")


@phase12_payments_router.get("/transactions")
async def get_all_transactions(
    status: Optional[str] = None,
    item_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """
    Get all transactions with optional filters (for admin use)
    """
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        if item_type:
            query["item_type"] = item_type
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Fetch transactions
        transactions = list(
            db.transactions.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Count total
        total = db.transactions.count_documents(query)
        
        return {
            "success": True,
            "transactions": transactions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")


@phase12_payments_router.get("/config")
async def get_payment_config():
    """
    Get payment configuration (public endpoint)
    Returns Razorpay Key ID needed for frontend integration
    """
    return {
        "enabled": bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and RAZORPAY_KEY_ID != "your_razorpay_key_id_here"),
        "key_id": RAZORPAY_KEY_ID if RAZORPAY_KEY_ID and RAZORPAY_KEY_ID != "your_razorpay_key_id_here" else None,
        "currency": "INR",
        "payment_methods": ["card", "upi", "netbanking", "wallet"]
    }



# ==================== EMAIL HELPER FUNCTION ====================

async def send_payment_success_email_task(
    to_email: str,
    user_name: str,
    transaction_id: str,
    amount: float,
    item_name: str,
    payment_method: str
):
    """
    Background task to send payment success email
    """
    try:
        html_content = create_payment_success_email(
            user_name=user_name,
            transaction_id=transaction_id,
            amount=amount,
            item_name=item_name,
            payment_method=payment_method
        )
        
        await send_email_async(
            to_email=to_email,
            subject=f"Payment Successful - {item_name}",
            html_content=html_content
        )
        
        logger.info(f"Payment success email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send payment success email: {str(e)}")

