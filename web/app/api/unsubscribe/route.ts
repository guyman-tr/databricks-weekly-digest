import { NextRequest, NextResponse } from "next/server";
import { loadSubscribers, saveSubscribers } from "@/lib/subscribers";

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token");

  if (!token) {
    return new NextResponse(renderPage("Invalid Link", "No unsubscribe token provided."), {
      status: 400,
      headers: { "Content-Type": "text/html" },
    });
  }

  try {
    const data = await loadSubscribers();
    const idx = data.subscribers.findIndex((s) => s.token === token);

    if (idx === -1) {
      return new NextResponse(renderPage("Not Found", "This unsubscribe link is invalid or has already been used."), {
        status: 404,
        headers: { "Content-Type": "text/html" },
      });
    }

    data.subscribers.splice(idx, 1);
    await saveSubscribers(data);

    return new NextResponse(renderPage("Unsubscribed", "You've been removed from the mailing list. Sorry to see you go!"), {
      status: 200,
      headers: { "Content-Type": "text/html" },
    });
  } catch (err) {
    console.error("Unsubscribe error:", err);
    return new NextResponse(renderPage("Error", "Something went wrong. Please try again later."), {
      status: 500,
      headers: { "Content-Type": "text/html" },
    });
  }
}

function renderPage(title: string, message: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title} - Databricks Weekly</title>
  <style>
    body { margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #0B0D10; color: #e4e7ee; font-family: -apple-system, system-ui, sans-serif; }
    .card { text-align: center; max-width: 400px; padding: 48px 32px; }
    h1 { color: #FF3621; font-size: 28px; margin: 0 0 12px; }
    p { color: #8B92A5; line-height: 1.6; margin: 0 0 24px; }
    a { color: #FF3621; text-decoration: none; font-weight: 600; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="card">
    <h1>${title}</h1>
    <p>${message}</p>
    <a href="/">Back to Databricks Weekly</a>
  </div>
</body>
</html>`;
}
