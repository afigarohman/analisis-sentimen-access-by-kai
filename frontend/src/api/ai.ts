import { api } from "./client";

/* =========================
   TYPES
========================= */

export type SentimentPredictionResponse = {
  text: string;
  label: string;
  confidence: number;
  aspect: string;
};

export type ScrapeResponse = {
  message: string;
  imported: number;
  skipped_duplicates: number;
  requested: number;
};

export type TrainResponse = {
  message: string;
  accuracy: number;
  samples: number;
  artifacts_dir: string;
};

export type GenerateReplyResponse = {
  reply: string;
};

export type InsightSample = {
  text: string;
  aspect: string;
};

export type InsightResponse = {
  total_negative: number;
  aspect_distribution: Record<string, number>;
  top_issues: Array<{
    aspect: string;
    count: number;
  }>;
  samples: InsightSample[];
};

export type FeedbackItem = {
  text: string;
  aspect: string;
  sentiment: string;
  matched_keywords: string[];
};

export type FeedbackListResponse = {
  total: number;
  items: FeedbackItem[];
  truncated?: boolean;
  shown?: number;
};

/* =========================
   API FUNCTIONS
========================= */

export async function predictSentiment(text: string) {
  const { data } = await api.post<SentimentPredictionResponse>("/ai/predict", {
    text,
  });
  return data;
}

export async function scrapeReviews(count: number) {
  const { data } = await api.post<ScrapeResponse>("/ai/scrape", { count });
  return data;
}

export async function trainModel(samples?: number, maxFeatures?: number) {
  const { data } = await api.post<TrainResponse>("/ai/train", {
    samples: samples ?? null,
    max_features: maxFeatures ?? 5000,
  });
  return data;
}

export async function generateAIReply(content: string) {
  const { data } = await api.post<GenerateReplyResponse>("/ai/generate-reply", {
    content,
  });
  return data;
}

export async function getInsight(): Promise<InsightResponse> {
  const { data } = await api.get<InsightResponse>("/ai/insight");
  return data;
}

export async function getFeedbackList(): Promise<FeedbackListResponse> {
  const { data } = await api.get<FeedbackListResponse>("/ai/feedback");
  return data;
}