"use client";

import React, { useState } from "react";

interface AddProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (provider: { name: string; id: string; apiKey: string }) => void;
  translations: Record<string, any>;
}

export function AddProviderModalSimple({ isOpen, onClose, onAdd, translations }: AddProviderModalProps) {
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
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium">
                {translations.settings?.ai_providers?.name || "Provider Name"}
              </label>
              <input
                name="name"
                value={newProvider.name}
                onChange={handleProviderChange}
                required
                placeholder="Stability AI"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="space-y-2">
              <label className="block text-sm font-medium">Provider ID</label>
              <input
                name="id"
                value={newProvider.id}
                onChange={handleProviderChange}
                required
                placeholder="stability"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium">API Key (Optional)</label>
              <input
                name="apiKey"
                type="password"
                value={newProvider.apiKey}
                onChange={handleProviderChange}
                placeholder="Enter API key (optional)"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <button 
              type="button" 
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              {translations.settings?.ai_providers?.add_provider || "Add Provider"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
