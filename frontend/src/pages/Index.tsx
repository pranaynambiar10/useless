import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Download, Loader2 } from "lucide-react";
import { UPLOAD_ENDPOINT } from "@/config";
import { Form } from "@/components/ui/form";
import { FormFile } from "@/components/ui/form-file";

const formSchema = z.object({
  file: z.instanceof(File).refine((file) => file.size > 0, "Please upload an image."),
});

type FormValues = z.infer<typeof formSchema>;

const Index = () => {
  const { toast } = useToast();
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      file: new File([], ""),
    },
  });

  const file = form.watch("file");

  React.useEffect(() => {
    if (file && file.size > 0) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreview(null);
    }
  }, [file]);

  const onSubmit = async (values: FormValues) => {
    try {
      setIsLoading(true);
      const fd = new FormData();
      fd.append("file", values.file);
      const res = await fetch(UPLOAD_ENDPOINT, { method: "POST", body: fd });
      
      if (!res.ok) {
        const errorJson = await res.json();
        throw new Error(errorJson.detail || "An unknown error occurred");
      }

      const blob = await res.blob();
      const imageUrl = URL.createObjectURL(blob);
      setResultUrl(imageUrl);

      const memeDataHeader = res.headers.get("X-Meme-Data");
      if (memeDataHeader) {
        const memeData = JSON.parse(memeDataHeader);
        toast({ title: "Meme ready!", description: memeData.caption || "Success" });
      } else {
        toast({ title: "Meme ready!" });
      }

    } catch (err: any) {
      toast({
        title: "Oops!",
        description: err?.message || "Something went wrong.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="max-w-5xl mx-auto px-4 py-16 md:py-24">
        <div className="text-center animate-fade-in">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
            <span className="bg-gradient-to-r from-primary to-muted-foreground bg-clip-text text-transparent">
              Dirt to Meme Magic
            </span>
          </h1>
          <p className="mt-3 md:mt-4 text-lg md:text-xl text-muted-foreground">
            Drop any picture. We analyze it and spin up a meme like sorcery.
          </p>
        </div>

        <div className="mt-10 grid md:grid-cols-2 gap-6 items-start">
          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle>Upload Image</CardTitle>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4"
                >
                  {preview && (
                    <img
                      src={preview}
                      alt="Selected image preview"
                      className="mx-auto max-h-64 rounded-md object-contain"
                    />
                  )}
                  <FormFile name="file" />
                  <Button type="submit" disabled={isLoading} className="w-full">
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />{" "}
                        Creating Meme...
                      </>
                    ) : (
                      "Make Meme"
                    )}
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>

          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle>Your Meme</CardTitle>
            </CardHeader>
            <CardContent>
              {resultUrl ? (
                <div className="space-y-4">
                  <img
                    src={resultUrl}
                    alt="Generated meme"
                    loading="lazy"
                    className="w-full rounded-md shadow"
                  />
                  <div className="flex gap-3">
                    <a href={resultUrl} download className="w-full">
                      <Button className="w-full" variant="secondary">
                        <Download className="mr-2 h-4 w-4" /> Download Meme
                      </Button>
                    </a>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground">
                  Your masterpiece will appear here.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
};

export default Index;
