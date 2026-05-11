import { useState, useEffect } from "react";
import { apiFetchJson } from "@/lib/apiClient";
import type { User, Profile } from "@/types";

interface UseUserResult {
  user: User | null;
  profile: Profile | null;
  avatarUrl: string | null;
  avatarError: boolean;
  loading: boolean;
  refetch: () => void;
  logout: () => Promise<void>;
}

export function useUser(): UseUserResult {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [avatarError, setAvatarError] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [authResult, profileResult] = await Promise.all([
        apiFetchJson<User>("/auth/me"),
        apiFetchJson<Profile>("/profile/me"),
      ]);

      if (authResult.ok) {
        setUser(authResult.data);
      }

      if (profileResult.ok) {
        setProfile(profileResult.data);
        if (profileResult.data.avatar_url) {
          const timestamp = Date.now();
          setAvatarUrl(`${profileResult.data.avatar_url}?v=${timestamp}`);
          setAvatarError(false);
        }
      } else if (profileResult.status === 404) {
        setProfile(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
    setProfile(null);
    setAvatarUrl(null);
    setAvatarError(false);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    user,
    profile,
    avatarUrl,
    avatarError,
    loading,
    refetch: fetchData,
    logout,
  };
}