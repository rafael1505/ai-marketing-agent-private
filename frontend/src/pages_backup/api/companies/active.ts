import { NextApiRequest, NextApiResponse } from 'next';

// Define a mock company structure for fallback responses
const mockCompany = {
  id: 'test_company',
  name: 'Test Company',
  description: 'This is a test company for development',
  logo_url: '/placeholder-logo.png',
  brand_colors: ['#3B82F6', '#1E40AF', '#93C5FD'],
  active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Only GET methods are supported for this fallback endpoint
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    // Return the mock company
    console.log('Returning mock company data from Next.js API route');
    return res.status(200).json(mockCompany);
  } catch (error) {
    console.error('Error in company API route:', error);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
}
