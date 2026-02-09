import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def seed_data():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("Seeding data...")
    
    # Seed Events
    events = [
        {
            "id": "event-1",
            "title": "Understanding Anxiety: Expert Panel",
            "description": "Join our panel of expert psychologists for an in-depth discussion on understanding and managing anxiety in modern life.",
            "event_type": "panel",
            "date": "February 15, 2025",
            "time": "7:00 PM EST",
            "price": "$25",
            "is_paid": True,
            "schedule": "Monthly",
            "features": ["Live Q&A sessions", "Expert panel of 3-5 psychologists", "Recorded for later viewing", "Certificate of attendance"],
            "is_active": True
        },
        {
            "id": "event-2",
            "title": "Mindfulness Workshop for Beginners",
            "description": "Learn practical mindfulness techniques that you can incorporate into your daily routine to manage stress effectively.",
            "event_type": "seminar",
            "date": "February 18, 2025",
            "time": "10:00 AM EST",
            "price": "$50",
            "is_paid": True,
            "schedule": "Weekly",
            "features": ["Interactive learning", "Practical exercises", "Take-home materials", "Small group format"],
            "is_active": True
        },
        {
            "id": "event-3",
            "title": "Open Circle: New Year, New Mindset",
            "description": "Free, community-led discussions in a safe and supportive environment. Share your thoughts and connect with others.",
            "event_type": "circle",
            "date": "February 20, 2025",
            "time": "6:00 PM EST",
            "price": "Free",
            "is_paid": False,
            "schedule": "Weekly",
            "features": ["Open to everyone", "Peer support format", "Various topics", "No registration needed"],
            "is_active": True
        },
        {
            "id": "event-4",
            "title": "Gaming Night: Community Connect",
            "description": "Virtual gaming sessions to build community and reduce stress together in a casual, fun environment.",
            "event_type": "gaming",
            "date": "February 22, 2025",
            "time": "8:00 PM EST",
            "price": "Free",
            "is_paid": False,
            "schedule": "Weekly",
            "features": ["Casual gaming environment", "Community building", "Stress relief", "All skill levels welcome"],
            "is_active": True
        }
    ]
    
    await db.events.delete_many({})
    await db.events.insert_many(events)
    print(f"✅ Seeded {len(events)} events")
    
    # Seed Blogs
    blogs = [
        {
            "id": "blog-1",
            "title": "Understanding the Connection Between Sleep and Mental Health",
            "excerpt": "Sleep and mental health are deeply interconnected. Discover how improving your sleep habits can significantly impact your emotional well-being and cognitive function.",
            "content": "Sleep and mental health are deeply interconnected in ways that many people don't fully realize. Quality sleep is not just about feeling rested; it's a critical component of maintaining good mental health. When we don't get enough sleep, our brain's ability to regulate emotions becomes impaired, leading to increased irritability, anxiety, and even depression. Research has shown that people with insomnia are ten times more likely to develop depression than those who sleep well. The relationship works both ways - mental health conditions can disrupt sleep patterns, creating a challenging cycle. Understanding this connection is the first step toward breaking that cycle and improving both your sleep and mental well-being.",
            "author": "Dr. Sarah Mitchell",
            "category": "Wellness",
            "read_time": "8 min read",
            "featured": True,
            "is_published": True
        },
        {
            "id": "blog-2",
            "title": "5 Mindfulness Techniques for Daily Stress Relief",
            "excerpt": "Simple, practical mindfulness exercises you can incorporate into your daily routine to manage stress effectively.",
            "content": "Mindfulness doesn't have to be complicated or time-consuming. These five simple techniques can be practiced anywhere, anytime, to help you manage stress and stay grounded. 1) Deep breathing exercises - Take 5 minutes to focus solely on your breath. 2) Body scan meditation - Notice sensations throughout your body without judgment. 3) Mindful walking - Pay attention to each step and your surroundings. 4) Gratitude journaling - Write down three things you're grateful for each day. 5) Single-tasking - Focus on one activity at a time, giving it your full attention. Regular practice of these techniques can significantly reduce stress levels and improve overall well-being.",
            "author": "Dr. Emily Rodriguez",
            "category": "Mindfulness",
            "read_time": "5 min read",
            "featured": False,
            "is_published": True
        },
        {
            "id": "blog-3",
            "title": "Navigating Anxiety in the Digital Age",
            "excerpt": "How our constant connection to technology affects anxiety levels and strategies to create healthy digital boundaries.",
            "content": "In today's hyperconnected world, our relationship with technology can significantly impact our mental health. The constant stream of notifications, social media comparisons, and 24/7 availability can contribute to heightened anxiety levels. Learning to set healthy boundaries with technology is crucial for managing anxiety. Start by designating tech-free times, especially before bed and during meals. Use app timers to limit social media use. Practice the '20-20-20 rule' - every 20 minutes, look at something 20 feet away for 20 seconds. Consider a digital detox weekend once a month. Remember, technology should enhance your life, not control it. By creating intentional boundaries, you can reduce anxiety and reclaim your mental peace.",
            "author": "Dr. James Chen",
            "category": "Anxiety",
            "read_time": "7 min read",
            "featured": False,
            "is_published": True
        },
        {
            "id": "blog-4",
            "title": "The Power of Vulnerability in Relationships",
            "excerpt": "Why emotional vulnerability strengthens connections and how to practice it safely in your relationships.",
            "content": "Vulnerability is often seen as a weakness, but in reality, it's one of the greatest strengths in building meaningful relationships. When we allow ourselves to be vulnerable - to share our fears, insecurities, and authentic selves - we create space for deeper connection and intimacy. Research by Dr. Brené Brown has shown that vulnerability is the birthplace of love, belonging, and joy. However, vulnerability must be practiced with discernment. Start small, sharing with people who have earned your trust. Notice how it feels to be seen and accepted for who you truly are. Remember that being vulnerable doesn't mean oversharing or having no boundaries. It means being honest about your emotions and needs, which ultimately strengthens your relationships and your sense of self.",
            "author": "Dr. Sarah Mitchell",
            "category": "Relationships",
            "read_time": "6 min read",
            "featured": False,
            "is_published": True
        },
        {
            "id": "blog-5",
            "title": "Building Resilience: Lessons from Cognitive Behavioral Therapy",
            "excerpt": "Key CBT principles that can help you develop mental resilience and cope with life's challenges.",
            "content": "Cognitive Behavioral Therapy (CBT) offers powerful tools for building mental resilience. At its core, CBT teaches us that our thoughts, feelings, and behaviors are interconnected, and by changing our thought patterns, we can influence our emotional responses and actions. Key principles include: 1) Recognizing cognitive distortions like all-or-nothing thinking and catastrophizing. 2) Challenging negative thoughts with evidence and alternative perspectives. 3) Behavioral activation - engaging in activities that bring meaning and joy. 4) Problem-solving skills to address challenges systematically. 5) Exposure to fears in a gradual, controlled way. These techniques aren't just for therapy sessions - they're practical skills you can use daily to build resilience, manage stress, and navigate life's inevitable challenges with greater confidence and clarity.",
            "author": "Dr. Emily Rodriguez",
            "category": "Therapy",
            "read_time": "9 min read",
            "featured": False,
            "is_published": True
        },
        {
            "id": "blog-6",
            "title": "Understanding Burnout: Signs, Causes, and Recovery",
            "excerpt": "A comprehensive guide to recognizing burnout symptoms and evidence-based strategies for recovery.",
            "content": "Burnout is more than just feeling tired - it's a state of chronic physical and emotional exhaustion that can seriously impact your health and quality of life. Common signs include feeling drained and unable to cope, decreased satisfaction and sense of accomplishment, cynicism and detachment, and physical symptoms like headaches or sleep problems. Burnout often results from prolonged stress, lack of control, unclear expectations, or mismatched values. Recovery requires addressing the root causes, not just the symptoms. Set clear boundaries between work and personal time. Practice regular self-care activities. Seek support from friends, family, or a therapist. Consider whether changes in your work environment or role might be necessary. Remember, recovery from burnout is possible, but it requires acknowledging the problem and taking active steps toward change.",
            "author": "Michael Thompson",
            "category": "Wellness",
            "read_time": "10 min read",
            "featured": False,
            "is_published": True
        }
    ]
    
    await db.blogs.delete_many({})
    await db.blogs.insert_many(blogs)
    print(f"✅ Seeded {len(blogs)} blogs")
    
    # Seed Careers
    careers = [
        {
            "id": "career-1",
            "title": "Licensed Clinical Psychologist",
            "department": "Clinical Services",
            "location": "Remote / Hybrid",
            "employment_type": "full-time",
            "description": "We're seeking a compassionate and experienced Licensed Clinical Psychologist to join our growing team. You'll provide individual and group therapy to clients dealing with various mental health challenges.",
            "responsibilities": [
                "Conduct psychological assessments and diagnostic evaluations",
                "Provide individual and group therapy sessions",
                "Develop and implement treatment plans",
                "Maintain accurate client records and documentation",
                "Collaborate with interdisciplinary team members"
            ],
            "qualifications": [
                "Doctoral degree (Ph.D. or Psy.D.) in Clinical Psychology",
                "Active state license to practice psychology",
                "3+ years of clinical experience",
                "Experience with diverse populations",
                "Strong interpersonal and communication skills"
            ],
            "benefits": ["Competitive salary", "Health insurance", "Flexible schedule", "Professional development opportunities"],
            "is_active": True
        },
        {
            "id": "career-2",
            "title": "Mental Health Counselor",
            "department": "Counseling Services",
            "location": "Remote",
            "employment_type": "full-time",
            "description": "Join our team as a Mental Health Counselor and make a real difference in people's lives. We're looking for someone who is passionate about mental health advocacy and client-centered care.",
            "responsibilities": [
                "Provide counseling services to individuals and groups",
                "Develop treatment plans in collaboration with clients",
                "Maintain confidential client records",
                "Participate in case consultations and team meetings",
                "Stay current with best practices in mental health counseling"
            ],
            "qualifications": [
                "Master's degree in Counseling or related field",
                "State license (LPC, LMHC, or equivalent)",
                "2+ years of counseling experience",
                "Knowledge of various therapeutic modalities",
                "Excellent listening and empathy skills"
            ],
            "benefits": ["Competitive compensation", "Healthcare benefits", "Work-life balance", "Continuing education support"],
            "is_active": True
        },
        {
            "id": "career-3",
            "title": "Community Outreach Coordinator",
            "department": "Community Engagement",
            "location": "Hybrid",
            "employment_type": "full-time",
            "description": "We're seeking an enthusiastic Community Outreach Coordinator to expand our reach and build partnerships within the community. This role is perfect for someone passionate about mental health advocacy.",
            "responsibilities": [
                "Develop and implement community outreach strategies",
                "Build relationships with community organizations",
                "Organize and facilitate mental health awareness events",
                "Create educational materials and presentations",
                "Track and report on outreach metrics"
            ],
            "qualifications": [
                "Bachelor's degree in Social Work, Psychology, or related field",
                "2+ years of experience in community outreach or engagement",
                "Strong communication and presentation skills",
                "Experience in mental health advocacy preferred",
                "Proficiency in social media and digital marketing"
            ],
            "benefits": ["Competitive salary", "Health benefits", "Flexible schedule", "Professional growth opportunities"],
            "is_active": True
        }
    ]
    
    await db.careers.delete_many({})
    await db.careers.insert_many(careers)
    print(f"✅ Seeded {len(careers)} career postings")
    
    print("\n🎉 Database seeding completed successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
