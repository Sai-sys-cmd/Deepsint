import { z } from "zod";

export const searchSchema = z.object({
  username: z
    .string()
    .min(1, "Username is required")
    .min(2, "Username must be at least 2 characters")
    .max(50, "Username too long")
    .regex(/^[a-zA-Z0-9._-]+$/, "Username contains invalid characters"),
  
  email: z
    .string()
    .email("Please enter a valid email")
    .optional()
    .or(z.literal("")),
  
  name: z
    .string()
    .max(100, "Name too long")
    .optional()
    .or(z.literal("")),
});

/**
 * @typedef {Object} SearchFormData
 * @property {string} username - Required username field
 * @property {string} [email] - Optional email field
 * @property {string} [name] - Optional name field
 */