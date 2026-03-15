import {
  S3Client,
  GetObjectCommand,
  PutObjectCommand,
} from "@aws-sdk/client-s3";

export interface Subscriber {
  email: string;
  status: "pending" | "confirmed";
  token: string;
  subscribedAt: string;
  confirmedAt?: string;
}

interface SubscribersData {
  subscribers: Subscriber[];
}

const SUBSCRIBERS_KEY = "subscribers.json";

function getR2Client(): S3Client {
  const accountId = process.env.R2_ACCOUNT_ID;
  const accessKeyId = process.env.R2_ACCESS_KEY_ID;
  const secretAccessKey = process.env.R2_SECRET_ACCESS_KEY;

  if (!accountId || !accessKeyId || !secretAccessKey) {
    throw new Error(
      `R2 credentials missing: accountId=${!!accountId}, accessKey=${!!accessKeyId}, secret=${!!secretAccessKey}`
    );
  }

  return new S3Client({
    region: "auto",
    endpoint: `https://${accountId}.r2.cloudflarestorage.com`,
    credentials: { accessKeyId, secretAccessKey },
  });
}

function getBucket(): string {
  return process.env.R2_BUCKET_NAME || "databricksdigest";
}

export async function loadSubscribers(): Promise<SubscribersData> {
  const client = getR2Client();
  try {
    const res = await client.send(
      new GetObjectCommand({ Bucket: getBucket(), Key: SUBSCRIBERS_KEY })
    );
    const body = await res.Body?.transformToString();
    return body ? JSON.parse(body) : { subscribers: [] };
  } catch (err: unknown) {
    const code = (err as { name?: string }).name;
    if (code === "NoSuchKey" || code === "NotFound") {
      return { subscribers: [] };
    }
    throw err;
  }
}

export async function saveSubscribers(data: SubscribersData): Promise<void> {
  const client = getR2Client();
  await client.send(
    new PutObjectCommand({
      Bucket: getBucket(),
      Key: SUBSCRIBERS_KEY,
      Body: JSON.stringify(data, null, 2),
      ContentType: "application/json",
    })
  );
}

export function generateToken(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}
