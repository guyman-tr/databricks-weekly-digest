import { NextRequest, NextResponse } from "next/server";
import {
  loadSubscribers,
  saveSubscribers,
  generateToken,
} from "@/lib/subscribers";
import { sendConfirmationEmail } from "@/lib/mailer";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const email = (body.email || "").trim().toLowerCase();

    if (!email || !EMAIL_RE.test(email)) {
      return NextResponse.json(
        { error: "Please enter a valid email address." },
        { status: 400 }
      );
    }

    const data = await loadSubscribers();
    const existing = data.subscribers.find((s) => s.email === email);

    if (existing?.status === "confirmed") {
      return NextResponse.json(
        { error: "This email is already subscribed." },
        { status: 409 }
      );
    }

    const token = generateToken();

    if (existing) {
      existing.token = token;
      existing.subscribedAt = new Date().toISOString();
    } else {
      data.subscribers.push({
        email,
        status: "pending",
        token,
        subscribedAt: new Date().toISOString(),
      });
    }

    await saveSubscribers(data);
    await sendConfirmationEmail(email, token);

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("Subscribe error:", err);
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    );
  }
}
