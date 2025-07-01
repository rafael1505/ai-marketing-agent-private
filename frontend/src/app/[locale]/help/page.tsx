import React from "react";
import { getTranslations } from "@/i18n";

interface HelpPageProps {
  params: {
    locale: string;
  };
}

export default function HelpPage({ params }: HelpPageProps) {
  const t = getTranslations(params.locale === "pt" ? "pt" : "en");

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border p-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
            {t.user_menu?.help_support || "Help & Support"}
          </h1>
          
          <div className="grid gap-8 md:grid-cols-2">
            {/* FAQ Section */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                Frequently Asked Questions
              </h2>
              <div className="space-y-4">
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    How do I create marketing materials?
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Navigate to the Materials section and click "Create New Material". You can then choose from various templates and customize them to your needs.
                  </p>
                </div>
                
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    How do I manage my account settings?
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Click on your profile picture in the top-right corner and select "Account Settings" to update your profile information and preferences.
                  </p>
                </div>
                
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    Can I collaborate with team members?
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Yes! You can share materials with your team members and collaborate on projects. Use the sharing options in each material.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Contact Support */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                Contact Support
              </h2>
              <div className="space-y-4">
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    📧 Email Support
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Get help via email within 24 hours
                  </p>
                  <a
                    href="mailto:support@aimarketingagent.com"
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                  >
                    support@aimarketingagent.com
                  </a>
                </div>
                
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    💬 Live Chat
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Available Monday-Friday, 9 AM - 6 PM EST
                  </p>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors">
                    Start Chat
                  </button>
                </div>
                
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    📚 Documentation
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Comprehensive guides and tutorials
                  </p>
                  <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm">
                    View Documentation
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* System Status */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              System Status
            </h2>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                All systems operational
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
