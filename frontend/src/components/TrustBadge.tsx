import { Shield, CheckCircle, Award } from "lucide-react";
import { cn } from "@/lib/utils";

interface TrustBadgeProps {
  type: "verified" | "certified" | "licensed";
  size?: "sm" | "md" | "lg";
  className?: string;
  showLabel?: boolean;
}

const badgeConfig = {
  verified: {
    icon: CheckCircle,
    label: "Verified Professional",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
  },
  certified: {
    icon: Award,
    label: "Certified Therapist",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  licensed: {
    icon: Shield,
    label: "Licensed Psychologist",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
  },
};

const sizeConfig = {
  sm: {
    iconSize: "w-3 h-3",
    padding: "px-2 py-1",
    fontSize: "text-xs",
  },
  md: {
    iconSize: "w-4 h-4",
    padding: "px-3 py-1.5",
    fontSize: "text-sm",
  },
  lg: {
    iconSize: "w-5 h-5",
    padding: "px-4 py-2",
    fontSize: "text-base",
  },
};

const TrustBadge = ({ type, size = "md", className, showLabel = true }: TrustBadgeProps) => {
  const config = badgeConfig[type];
  const sizes = sizeConfig[size];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium transition-all duration-200",
        config.bgColor,
        config.color,
        sizes.padding,
        sizes.fontSize,
        className
      )}
    >
      <Icon className={sizes.iconSize} />
      {showLabel && <span>{config.label}</span>}
    </div>
  );
};

export default TrustBadge;
