import * as React from "react";
import { useFormContext } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const FormFile = React.forwardRef<HTMLInputElement, InputProps>(({ ...props }, ref) => {
  const { name } = props;
  const { control } = useFormContext();

  if (!name) {
    return null;
  }

  return (
    <FormField
      control={control}
      name={name}
      render={({ field: { onChange, value, ...field } }) => (
        <FormItem>
          <FormLabel>Picture</FormLabel>
          <FormControl>
            <Input
              {...field}
              {...props}
              type="file"
              accept="image/*"
              onChange={(event) => {
                onChange(event.target.files && event.target.files[0]);
              }}
              ref={ref}
            />
          </FormControl>
          <FormDescription>
            Upload a picture to be meme-ified.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );
});

FormFile.displayName = "FormFile";

export { FormFile };
