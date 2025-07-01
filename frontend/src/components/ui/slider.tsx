"use client";

import * as React from "react";

interface SliderProps {
  min?: number;
  max?: number;
  step?: number;
  value: number[];
  onValueChange: (value: number[]) => void;
  className?: string;
  id?: string;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, min = 0, max = 100, step = 1, value, onValueChange, id, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseFloat(e.target.value);
      onValueChange([newValue]);
    };

    return (
      <div className={`relative flex w-full touch-none select-none items-center ${className || ""}`}>
        <input
          ref={ref}
          id={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[0] || 0}
          onChange={handleChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          {...props}
        />
        <style jsx>{`
          .slider::-webkit-slider-thumb {
            appearance: none;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: #2563eb;
            cursor: pointer;
            border: 2px solid #ffffff;
            box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
          }
          .slider::-moz-range-thumb {
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: #2563eb;
            cursor: pointer;
            border: 2px solid #ffffff;
            box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
          }
        `}</style>
      </div>
    );
  }
);

Slider.displayName = "Slider";

export { Slider };
