import { api } from "./client";

export type SentimentPredictionResponse = {
  text: string;
  result: {
    label: string;
    confidence: number;
  };
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
  const { data } = await api.post("/ai/generate-reply", {
    content,
  });

  return data;
}