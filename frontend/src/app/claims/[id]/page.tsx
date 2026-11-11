import ClaimDetailClient from "./client";

export default async function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ClaimDetailClient id={id} />;
}