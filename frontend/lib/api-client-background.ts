/**
 * API Client for Background Job Processing
 * Handles long-running analysis without timeout issues
 */

import { config, getFullApiUrl } from "./config";

export interface JobStatus {
  job_id: string;
  status: "processing" | "complete" | "failed";
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface StartJobResponse {
  job_id: string;
  status: string;
  message: string;
}

/**
 * Custom error for job timeout
 */
export class JobTimeoutError extends Error {
  constructor(
    message: string,
    public jobId: string,
    public elapsedMinutes: number
  ) {
    super(message);
    this.name = "JobTimeoutError";
  }
}

/**
 * Start analysis job in background
 * Returns immediately with job_id
 */
export async function startAnalysisJob(
  formData: FormData
): Promise<StartJobResponse> {
  const url = getFullApiUrl(config.api.endpoints.startAnalysis);

  console.log("[API CLIENT] Starting background job:", url);

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  const data = await response.json();
  console.log("[API CLIENT] Job started:", data);

  return data;
}

/**
 * Poll job status
 * Call repeatedly until status is "complete" or "failed"
 */
export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const url = getFullApiUrl(`${config.api.endpoints.jobStatus}/${jobId}`);

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Job ${jobId} not found`);
    }
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return await response.json();
}

/**
 * Get job results (once complete)
 */
export async function getJobResults(jobId: string): Promise<any> {
  const url = getFullApiUrl(`${config.api.endpoints.jobResults}/${jobId}`);

  console.log("[API CLIENT] Fetching results for job:", jobId);

  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 202) {
      throw new Error("Job is still processing");
    }
    if (response.status === 404) {
      throw new Error(`Results not found for job ${jobId}`);
    }
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  const data = await response.json();
  console.log("[API CLIENT] Results fetched successfully");

  return data;
}

/**
 * Poll job status until complete
 * Resolves with final status when done
 * Throws JobTimeoutError if polling exceeds maxPolls
 */
export async function pollUntilComplete(
  jobId: string,
  onProgress?: (status: JobStatus) => void,
  pollInterval: number = 5000,
  maxPolls: number = 360 // 30 minutes (360 * 5s = 1800s)
): Promise<JobStatus> {
  console.log(
    `[API CLIENT] Starting to poll job ${jobId} every ${pollInterval}ms (max ${maxPolls} polls)`
  );

  let pollCount = 0;

  while (pollCount < maxPolls) {
    pollCount++;
    const status = await getJobStatus(jobId);

    // Call progress callback
    if (onProgress) {
      onProgress(status);
    }

    // Check if done
    if (status.status === "complete" || status.status === "failed") {
      console.log(
        `[API CLIENT] Job ${jobId} finished with status: ${status.status} after ${pollCount} polls`
      );
      return status;
    }

    // Log progress every 12 polls (1 minute)
    if (pollCount % 12 === 0) {
      const elapsedMinutes = Math.floor((pollCount * pollInterval) / 60000);
      console.log(
        `[API CLIENT] Job ${jobId} still processing... (${elapsedMinutes} min elapsed, ${status.progress}% complete)`
      );
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, pollInterval));
  }

  // Timeout reached
  const elapsedMinutes = Math.floor((maxPolls * pollInterval) / 60000);
  console.error(
    `[API CLIENT] Job ${jobId} timed out after ${elapsedMinutes} minutes (${maxPolls} polls)`
  );
  throw new JobTimeoutError(
    `Analysis timed out after ${elapsedMinutes} minutes. The job may still be processing on the server.`,
    jobId,
    elapsedMinutes
  );
}

/**
 * Full workflow: Start job, poll until complete, get results
 */
export async function runAnalysisWithPolling(
  formData: FormData,
  onProgress?: (status: JobStatus) => void
): Promise<any> {
  // Step 1: Start job
  const { job_id } = await startAnalysisJob(formData);

  // Step 2: Poll until complete
  const finalStatus = await pollUntilComplete(job_id, onProgress);

  // Step 3: Check if failed
  if (finalStatus.status === "failed") {
    throw new Error(finalStatus.error || "Job failed");
  }

  // Step 4: Get results
  const results = await getJobResults(job_id);

  return results;
}
