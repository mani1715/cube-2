import React, { createContext, useContext, useState, useEffect, ReactNode, useRef, useCallback } from "react";
import { adminAuthAPI } from "../lib/adminApi";
import { toast } from "sonner";

export interface AdminUser {
  id: string;
  email: string;
  role: "super_admin" | "admin" | "viewer";
  is_active: string;
  permissions: string[];
}

interface AdminContextType {
  admin: AdminUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  isSuperAdmin: () => boolean;
  isAdmin: () => boolean;
  isViewer: () => boolean;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

// Inactivity timeout: 30 minutes (in milliseconds)
const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes
// Warning before logout: 2 minutes
const WARNING_TIMEOUT = 28 * 60 * 1000; // 28 minutes

export function AdminProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const inactivityTimerRef = useRef<NodeJS.Timeout | null>(null);
  const warningTimerRef = useRef<NodeJS.Timeout | null>(null);
  const warningShownRef = useRef<boolean>(false);

  // Clear all timers
  const clearTimers = useCallback(() => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
      inactivityTimerRef.current = null;
    }
    if (warningTimerRef.current) {
      clearTimeout(warningTimerRef.current);
      warningTimerRef.current = null;
    }
    warningShownRef.current = false;
  }, []);

  // Reset inactivity timer
  const resetInactivityTimer = useCallback(() => {
    if (!admin) return;

    clearTimers();

    // Set warning timer (2 minutes before auto-logout)
    warningTimerRef.current = setTimeout(() => {
      if (!warningShownRef.current) {
        warningShownRef.current = true;
        toast.warning("Session Expiring Soon", {
          description: "You will be logged out in 2 minutes due to inactivity.",
          duration: 10000,
        });
      }
    }, WARNING_TIMEOUT);

    // Set auto-logout timer (30 minutes)
    inactivityTimerRef.current = setTimeout(async () => {
      toast.error("Session Expired", {
        description: "You have been logged out due to inactivity.",
        duration: 5000,
      });
      await logout();
      window.location.href = "/admin/login";
    }, INACTIVITY_TIMEOUT);
  }, [admin]);

  // Track user activity
  useEffect(() => {
    if (!admin) {
      clearTimers();
      return;
    }

    // List of events to track for user activity
    const events = ["mousedown", "keydown", "scroll", "touchstart", "click"];

    const handleActivity = () => {
      resetInactivityTimer();
    };

    // Initialize timer
    resetInactivityTimer();

    // Add event listeners
    events.forEach((event) => {
      window.addEventListener(event, handleActivity);
    });

    // Cleanup
    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, handleActivity);
      });
      clearTimers();
    };
  }, [admin, resetInactivityTimer, clearTimers]);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("adminToken");
      
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const adminData = await adminAuthAPI.getCurrentAdmin();
        setAdmin(adminData);
      } catch (error) {
        console.error("Auth check failed:", error);
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminRefreshToken");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      await adminAuthAPI.login(email, password);
      const adminData = await adminAuthAPI.getCurrentAdmin();
      setAdmin(adminData);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      clearTimers(); // Clear inactivity timers
      await adminAuthAPI.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setAdmin(null);
      localStorage.removeItem("adminToken");
      localStorage.removeItem("adminRefreshToken");
    }
  };

  const hasPermission = (permission: string): boolean => {
    if (!admin) return false;
    return admin.permissions.includes(permission);
  };

  const isSuperAdmin = (): boolean => {
    return admin?.role === "super_admin";
  };

  const isAdmin = (): boolean => {
    return admin?.role === "admin" || admin?.role === "super_admin";
  };

  const isViewer = (): boolean => {
    return admin?.role === "viewer";
  };

  return (
    <AdminContext.Provider
      value={{
        admin,
        loading,
        login,
        logout,
        hasPermission,
        isSuperAdmin,
        isAdmin,
        isViewer,
      }}
    >
      {children}
    </AdminContext.Provider>
  );
}

export function useAdmin() {
  const context = useContext(AdminContext);
  if (context === undefined) {
    throw new Error("useAdmin must be used within an AdminProvider");
  }
  return context;
}
