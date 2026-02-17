import { ReactNode, forwardRef } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

interface LayoutProps {
  children: ReactNode;
  showFooter?: boolean;
}

export const Layout = forwardRef<HTMLDivElement, LayoutProps>(
  ({ children, showFooter = true }, ref) => {
    return (
      <div ref={ref} className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 pt-16 md:pt-20 page-transition">{children}</main>
        {showFooter && <Footer />}
      </div>
    );
  }
);

Layout.displayName = "Layout";
