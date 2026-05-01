import ResetPasswordForm from "./ResetPasswordForm";

type ResetPasswordPageProps = {
  searchParams?: { token?: string | string[] };
};

export default function ResetPasswordPage({ searchParams }: ResetPasswordPageProps) {
  const tokenParam = searchParams?.token;
  const initialToken = Array.isArray(tokenParam) ? tokenParam[0] ?? "" : tokenParam ?? "";

  return <ResetPasswordForm initialToken={initialToken} />;
}
