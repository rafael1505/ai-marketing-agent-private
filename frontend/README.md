# AI Marketing Agent Frontend

This is the frontend for the AI Marketing Agent application. It's built with Next.js, React, and Tailwind CSS.

## Features

- Three-stage material creation workflow (Idea, Refinement, Finalization)
- Material management
- Company configuration
- Integration with AI image generation services
- Internationalization support (English and Brazilian Portuguese)
- Responsive, modern UI

## Getting Started

First, make sure the backend API is running. Then, start the development server:

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) with your browser to see the result.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for API client standards (UUID correlation IDs, defensive URL normalization), isomorphic base URL, and the Materials module’s use of the real backend API (no localStorage mocks).

## Project Structure

- `src/app` - Next.js App Router pages
- `src/components` - Reusable React components
- `src/services` - API integration services
- `src/types` - TypeScript type definitions
- `src/i18n` - Internationalization resources
- `src/lib` - Utility functions
- `src/constants` - Application constants

## Running with Docker

To run the entire application stack with Docker Compose:

```bash
cd .. # Navigate to the project root
docker-compose up
```

This will start the frontend, backend API, and MongoDB.

## Technologies Used

- Next.js 14
- React
- TypeScript
- Tailwind CSS
- Axios

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
