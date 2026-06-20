import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "AgTech UNS",
  description: "Plataforma de gestión agropecuaria",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
