"use client";

import React, { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AddProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (provider: { name: string; id: string; apiKey: string }) => void;
  translations: Record<string, any>;
}

export function AddProviderModal({ isOpen, onClose, onAdd, translations }: AddProviderModalProps) {
  const [newProvider, setNewProvider] = useState({ name: "", id: "", apiKey: "" });

  const handleProviderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewProvider(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newProvider.name && newProvider.id) {
      onAdd(newProvider);
      setNewProvider({ name: "", id: "", apiKey: "" });
      onClose();
    }
  };

  const handleClose = () => {
    setNewProvider({ name: "", id: "", apiKey: "" });
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">
            {translations.settings?.ai_providers?.add || "Add Provider"}
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="modal-provider-name">
                {translations.settings?.ai_providers?.name || "Provider Name"}
              </Label>
              <Input
                id="modal-provider-name"
                name="name"
                value={newProvider.name}
                onChange={handleProviderChange}
                required
                placeholder="Stability AI"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="modal-provider-id">Provider ID</Label>
              <Input
                id="modal-provider-id"
                name="id"
                value={newProvider.id}
                onChange={handleProviderChange}
                required
                placeholder="stability"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="modal-provider-api-key">API Key (Optional)</Label>
              <Input
                id="modal-provider-api-key"
                name="apiKey"
                type="password"
                value={newProvider.apiKey}
                onChange={handleProviderChange}
                placeholder="Enter API key (optional)"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit">
              {translations.settings?.ai_providers?.add_provider || "Add Provider"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
