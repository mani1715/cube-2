import { useState, forwardRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, X, Heart, User, LogOut, LayoutDashboard, LogIn, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useUser } from "@/contexts/UserContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const navLinks = [
  { name: "Home", path: "/" },
  { name: "About", path: "/about" },
  { name: "Services", path: "/services" },
  { name: "Events", path: "/events" },
  { name: "Blogs", path: "/blogs" },
  { name: "Careers", path: "/careers" },
];

export const Navbar = forwardRef<HTMLElement>((_, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useUser();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <nav 
      ref={ref} 
      className="fixed top-0 left-0 right-0 z-50 bg-background/90 backdrop-blur-lg border-b border-border/50"
      id="main-navigation"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          <Link 
            to="/" 
            className="flex items-center gap-2 group"
            aria-label="A-Cube home page"
          >
            <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center group-hover:scale-105 transition-transform duration-300 shadow-soft group-hover:shadow-glow">
              <Heart className="w-5 h-5 text-primary-foreground" aria-hidden="true" />
            </div>
            <span className="font-display text-xl font-semibold text-foreground">
              A-Cube
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1" role="menubar">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                role="menuitem"
                aria-current={location.pathname === link.path ? "page" : undefined}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  location.pathname === link.path
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <ThemeToggle />
            <Link to="/volunteer">
              <Button variant="outline" size="sm" aria-label="Become a volunteer">
                Volunteer
              </Button>
            </Link>
            
            {/* User Authentication Section */}
            {isAuthenticated && user ? (
              // User Dropdown Menu
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    className="relative h-9 w-9 rounded-full"
                    aria-label={`User menu for ${user.name}`}
                  >
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {getUserInitials(user.name)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/user/dashboard')}>
                    <LayoutDashboard className="mr-2 h-4 w-4" aria-hidden="true" />
                    <span>Dashboard</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/user/profile')}>
                    <User className="mr-2 h-4 w-4" aria-hidden="true" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                    <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              // Login & Signup Buttons
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm" aria-label="Login to your account">
                    <LogIn className="w-4 h-4 mr-2" aria-hidden="true" />
                    Login
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button variant="hero" size="sm" aria-label="Create new account">
                    <UserPlus className="w-4 h-4 mr-2" aria-hidden="true" />
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-foreground hover:bg-muted rounded-lg transition-colors touch-target"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? "Close menu" : "Open menu"}
            aria-expanded={isOpen}
            aria-controls="mobile-menu"
          >
            {isOpen ? <X className="w-6 h-6" aria-hidden="true" /> : <Menu className="w-6 h-6" aria-hidden="true" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div 
            className="md:hidden py-4 border-t border-border animate-fade-in"
            id="mobile-menu"
            role="menu"
            aria-label="Mobile navigation menu"
          >
            <div className="flex flex-col gap-2">
              {navLinks.map((link, index) => (
                <Link
                  key={link.path}
                  to={link.path}
                  role="menuitem"
                  aria-current={location.pathname === link.path ? "page" : undefined}
                  onClick={() => setIsOpen(false)}
                  className={`px-4 py-3 rounded-lg text-sm font-medium transition-all duration-300 animate-slide-in-up ${
                    location.pathname === link.path
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  {link.name}
                </Link>
              ))}
              <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-border">
                <div className="flex items-center justify-between px-4 mb-2">
                  <span className="text-sm font-medium text-muted-foreground">Theme</span>
                  <ThemeToggle />
                </div>
                
                {/* Mobile User Section */}
                {isAuthenticated && user ? (
                  <>
                    <div className="px-4 py-2 mb-2" role="status" aria-live="polite">
                      <p className="text-sm font-medium">{user.name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                    <Link to="/user/dashboard" onClick={() => setIsOpen(false)}>
                      <Button variant="outline" className="w-full justify-start" aria-label="Go to dashboard">
                        <LayoutDashboard className="w-4 h-4 mr-2" aria-hidden="true" />
                        Dashboard
                      </Button>
                    </Link>
                    <Link to="/user/profile" onClick={() => setIsOpen(false)}>
                      <Button variant="outline" className="w-full justify-start" aria-label="View profile">
                        <User className="w-4 h-4 mr-2" aria-hidden="true" />
                        Profile
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-destructive"
                      onClick={() => {
                        setIsOpen(false);
                        handleLogout();
                      }}
                      aria-label="Logout from account"
                    >
                      <LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
                      Logout
                    </Button>
                  </>
                ) : (
                  <>
                    <Link to="/login" onClick={() => setIsOpen(false)}>
                      <Button variant="outline" className="w-full justify-start" aria-label="Login to your account">
                        <LogIn className="w-4 h-4 mr-2" aria-hidden="true" />
                        Login
                      </Button>
                    </Link>
                    <Link to="/signup" onClick={() => setIsOpen(false)}>
                      <Button variant="hero" className="w-full" aria-label="Create new account">
                        <UserPlus className="w-4 h-4 mr-2" aria-hidden="true" />
                        Sign Up
                      </Button>
                    </Link>
                  </>
                )}
                
                <Link to="/volunteer" onClick={() => setIsOpen(false)}>
                  <Button variant="outline" className="w-full" aria-label="Become a volunteer">
                    Volunteer
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
});

Navbar.displayName = "Navbar";