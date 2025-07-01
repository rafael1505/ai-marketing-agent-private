import { useEffect, useState } from 'react';

/**
 * Custom hook for handling image loading with preloading and caching
 * Helps prevent image flickering by preloading images
 * Now returns the error state for better error handling
 */
export function useImageLoader(url: string | undefined, fallbackUrl: string = '/placeholder-logo.svg') {
  const [imageUrl, setImageUrl] = useState<string>(fallbackUrl);
  const [isLoading, setIsLoading] = useState<boolean>(!!url);
  const [error, setError] = useState<boolean>(false);
  
  useEffect(() => {
    if (!url) {
      setImageUrl(fallbackUrl);
      setIsLoading(false);
      setError(false);
      return;
    }
    
    // Skip for blob URLs as they are already loaded and should be displayed immediately
    if (url.startsWith('blob:')) {
      console.log('Using blob URL directly:', url);
      setImageUrl(url);
      setIsLoading(false);
      setError(false);
      return;
    }
    
    setIsLoading(true);
    
    const img = new Image();
    img.onload = () => {
      setImageUrl(url);
      setIsLoading(false);
      setError(false);
    };
    
    img.onerror = () => {
      console.log('Image failed to load:', url);
      setImageUrl(fallbackUrl);
      setIsLoading(false);
      setError(true);
    };
    
    img.src = url;
    
    return () => {
      // Cleanup
      img.onload = null;
      img.onerror = null;
    };
  }, [url, fallbackUrl]);
  
  return { imageUrl, isLoading, error };
}
