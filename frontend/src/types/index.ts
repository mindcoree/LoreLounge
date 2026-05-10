export interface User {
  id: string;
  email: string;
  role: string;
  coins?: number;
}

export interface Profile {
  name: string;
  bio: string | null;
  avatar_url: string | null;
  background_url: string | null;
  birth_date: string | null;
  gender: Gender | null;
}

export type Gender = "unspecified" | "male" | "female";

export interface UserWithProfile {
  user: User;
  profile: Profile | null;
}