"use client";

import { useState, useMemo } from "react";

interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  onError?: () => void;
}

const sizeClasses = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-11 w-11 text-base",
  xl: "h-16 w-16 text-xl",
};

const roundedClasses = {
  sm: "rounded-lg",
  md: "rounded-xl",
  lg: "rounded-xl",
  xl: "rounded-2xl",
};

export function Avatar({
  src,
  alt = "Аватар",
  fallback,
  size = "md",
  className = "",
  onError,
}: AvatarProps) {
  const [error, setError] = useState(false);
  const initials = useMemo(() => {
    if (!fallback) return "?";
    return fallback.charAt(0).toUpperCase();
  }, [fallback]);

  const handleError = () => {
    setError(true);
    onError?.();
  };

  if (src && !error) {
    return (
      <img
        src={src}
        alt={alt}
        className={`object-cover ${sizeClasses[size]} ${roundedClasses[size]} ${className}`}
        onError={handleError}
      />
    );
  }

  return (
    <div
      className={`flex items-center justify-center bg-gradient-to-br from-[#b7d4ff] to-[#6fc3a2] font-bold text-white ${sizeClasses[size]} ${roundedClasses[size]} ${className}`}
    >
      {initials}
    </div>
  );
}