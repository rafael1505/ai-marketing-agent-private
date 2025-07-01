"use client";

import React, { useState, useRef, KeyboardEvent, useEffect } from "react";
import { Input } from "./input";
import { Badge } from "./badge";
import { X } from "lucide-react";

interface TagInputProps {
  placeholder?: string;
  tags: string[];
  setTags: (tags: string[]) => void;
  disabled?: boolean;
  maxTags?: number;
}

export const TagInput = ({
  placeholder = "Add tag...",
  tags = [],
  setTags,
  disabled = false,
  maxTags = 10
}: TagInputProps) => {
  const [inputValue, setInputValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input element when tags change
  useEffect(() => {
    if (tags.length < maxTags && inputRef.current) {
      inputRef.current.focus();
    }
  }, [tags, maxTags]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    const trimmedInput = inputValue.trim();
    
    if ((e.key === "Enter" || e.key === " " || e.key === ",") && trimmedInput) {
      e.preventDefault();
      if (tags.length >= maxTags) return;
      
      // Don't add duplicate tags
      if (!tags.includes(trimmedInput)) {
        setTags([...tags, trimmedInput]);
      }
      setInputValue("");
    } else if (e.key === "Backspace" && !inputValue && tags.length > 0) {
      // Remove last tag when backspace is pressed and input is empty
      setTags(tags.slice(0, -1));
    }
  };

  const removeTag = (index: number) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  return (
    <div className="flex flex-wrap gap-1.5 p-1 border rounded-md bg-background focus-within:ring-1 focus-within:ring-ring">
      {tags.map((tag, index) => (
        <Badge key={index} variant="secondary" className="text-xs py-1">
          {tag}
          <button
            type="button"
            className="ml-1 hover:bg-muted rounded-full"
            onClick={() => removeTag(index)}
            disabled={disabled}
          >
            <X className="h-3 w-3" />
            <span className="sr-only">Remove {tag}</span>
          </button>
        </Badge>
      ))}
      
      {tags.length < maxTags && (
        <Input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-grow border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 p-1 h-7 text-sm"
          disabled={disabled}
        />
      )}
    </div>
  );
};
