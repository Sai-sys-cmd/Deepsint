"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { Search, Loader2, User, Mail, UserCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

import { searchSchema } from "@/lib/validations";
import { apiClient } from "@/lib/api-client";

export default function SearchForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const form = useForm({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      username: "",
      email: "",
      name: "",
    },
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Filter out empty optional fields
      const filteredData = {
        username: data.username,
        ...(data.email && { email: data.email }),
        ...(data.name && { name: data.name }),
      };

      const response = await apiClient.post("/api/search", filteredData);
      
      if (!response.data.success) {
        throw new Error(response.data.error || "Search failed");
      }

      // Navigate to results page with search ID
      router.push(`/results/${response.data.searchId}`);
      
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : "Failed to start search. Please try again.";
      setError(errorMessage);
      
      // Reset form on server errors
      if (errorMessage.includes("server")) {
        form.reset();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="w-full">
        <CardHeader className="space-y-1">
          <div className="flex items-center gap-2">
            <Search className="h-6 w-6 text-primary" />
            <CardTitle className="text-2xl">OSINT Intelligence Search</CardTitle>
          </div>
          <CardDescription>
            Search for digital footprints across multiple platforms. 
            Enter a username and optional details for comprehensive analysis.
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              {/* Username Field */}
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Username *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="alice_tech, john.doe, cybersec_expert..."
                        {...field}
                        disabled={isSubmitting}
                        className="text-base"
                      />
                    </FormControl>
                    <FormDescription>
                      Primary identifier to search across platforms (GitHub, Reddit, Twitter, etc.)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Email Field */}
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email Address
                      <span className="text-xs text-muted-foreground ml-1">(Optional)</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="alice@example.com"
                        {...field}
                        disabled={isSubmitting}
                        className="text-base"
                      />
                    </FormControl>
                    <FormDescription>
                      Cross-reference with breach databases and email-linked accounts
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Full Name Field */}
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <UserCheck className="h-4 w-4" />
                      Full Name
                      <span className="text-xs text-muted-foreground ml-1">(Optional)</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Alice Johnson, John Doe..."
                        {...field}
                        disabled={isSubmitting}
                        className="text-base"
                      />
                    </FormControl>
                    <FormDescription>
                      Enhance search accuracy and identify additional profiles
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Error Display */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full h-12 text-base font-semibold"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching across platforms...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Start Intelligence Search
                  </>
                )}
              </Button>

              {/* Search Info */}
              <div className="text-sm text-muted-foreground bg-muted/30 p-4 rounded-lg">
                <p className="font-medium mb-2">This search will query:</p>
                <ul className="space-y-1 list-disc list-inside ml-2">
                  <li>GitHub profiles and repositories</li>
                  <li>Reddit user activity and posts</li>
                  <li>Social media platforms (Twitter, LinkedIn)</li>
                  <li>Breach databases (HaveIBeenPwned)</li>
                  <li>Domain registration records</li>
                  <li>Public code repositories</li>
                </ul>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}