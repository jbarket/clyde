# Next.js Development Guidelines

## Next.js Project Structure

### Standard Directory Layout
- `pages/{index.tsx,_app.tsx,_document.tsx,api/}`
- `app/{layout.tsx,page.tsx,loading.tsx,error.tsx}` (App Router)
- `components/{shared,ui,forms}/`
- `lib/{utils.ts,validations.ts,db.ts}`
- `public/{images,icons,static-assets}/`
- `styles/{globals.css,components.module.css}`

## Routing Patterns

### Pages Router (Legacy)
- File-based routing in pages/ directory
- Dynamic routes with [id].tsx and [...slug].tsx
- API routes in pages/api/ directory
- Use getStaticProps, getServerSideProps, getStaticPaths for data fetching

### App Router (Recommended)
- File-based routing in app/ directory with layout nesting
- Server and client components with proper boundaries
- Route groups with (group-name) folders
- Parallel routes with @folder convention

### Dynamic Routing
- Use [param] for single dynamic segments
- Use [...param] for catch-all routes
- Use [[...param]] for optional catch-all routes
- Access params via useRouter() hook or params prop

## Data Fetching Patterns

### Server-Side Rendering (SSR)
- Use getServerSideProps for data that changes frequently
- Implement proper error handling and loading states
- Consider caching strategies for expensive operations
- Use for authenticated content and real-time data

### Static Site Generation (SSG)
- Use getStaticProps for static data that doesn't change often
- Use getStaticPaths for dynamic routes with known paths
- Implement incremental static regeneration (ISR) for data updates
- Ideal for marketing pages, blogs, and documentation

### Client-Side Fetching
- Use SWR or React Query for client-side data fetching
- Implement proper caching and revalidation strategies
- Handle loading states and error conditions
- Use for user-specific data and interactive features

### App Router Data Fetching
- Use async Server Components for server-side data fetching
- Implement loading.tsx and error.tsx for better UX
- Use React Suspense for streaming and progressive loading
- Cache data with fetch() and revalidation strategies

## Server Components vs Client Components

### Server Components (Default)
- Render on server, reducing client bundle size
- Access server-only APIs and databases directly
- Cannot use browser APIs or event handlers
- Ideal for static content and data fetching

### Client Components
- Use "use client" directive at file top
- Enable interactivity and browser APIs
- Can use hooks and event handlers
- Should be used sparingly for interactive elements

### Component Boundaries
- Keep server components as default when possible
- Push client boundaries down to leaf components
- Pass server data to client components via props
- Avoid mixing server and client logic in same component

## Performance Optimization

### Image Optimization
- Use next/image for automatic optimization
- Implement proper alt text and loading strategies
- Use priority prop for above-the-fold images
- Configure custom image loaders for external sources

### Font Optimization
- Use next/font for automatic font optimization
- Preload critical fonts to reduce layout shift
- Use font-display: swap for better perceived performance
- Consider variable fonts for reduced file sizes

### Bundle Optimization
- Use dynamic imports for code splitting
- Implement proper chunk strategies
- Analyze bundle with @next/bundle-analyzer
- Tree shake unused code and dependencies

### Core Web Vitals
- Monitor and optimize Largest Contentful Paint (LCP)
- Reduce Cumulative Layout Shift (CLS)
- Minimize First Input Delay (FID) / Interaction to Next Paint (INP)
- Use Next.js built-in performance metrics

## API Routes and Backend

### API Route Patterns
- Use pages/api/ or app/api/ for API endpoints
- Implement proper HTTP method handling (GET, POST, PUT, DELETE)
- Add input validation and error handling
- Use middleware for authentication and CORS

### Database Integration
- Use Prisma or similar ORM for type-safe database access
- Implement connection pooling for production
- Use environment variables for database configuration
- Consider edge runtime for global distribution

### Authentication
- Implement NextAuth.js for authentication providers
- Use JWT or session-based authentication
- Secure API routes with proper middleware
- Handle authentication state in client components

## Styling and UI

### CSS Strategies
- Use CSS Modules for component-scoped styles
- Implement Tailwind CSS for utility-first approach
- Consider styled-jsx for CSS-in-JS solution
- Use CSS custom properties for theming

### UI Libraries
- Integrate with Radix UI, Headless UI, or similar for accessible components
- Use Storybook for component development and documentation
- Implement consistent design system across application
- Consider shadcn/ui for pre-built component patterns

## State Management

### Global State
- Use Zustand or Redux Toolkit for complex state management
- Implement Context API for simple global state
- Consider server state libraries like React Query
- Use localStorage/sessionStorage for client-side persistence

### Form Handling
- Use React Hook Form for complex forms with validation
- Implement Zod for runtime type validation
- Handle server-side validation in API routes
- Provide proper error messaging and UX feedback

## Testing Strategies

### Unit Testing
- Use Jest and React Testing Library for component testing
- Test API routes with supertest or similar tools
- Mock external dependencies and database connections
- Implement snapshot testing for stable components

### End-to-End Testing
- Use Playwright or Cypress for E2E testing
- Test critical user flows and business logic
- Implement visual regression testing
- Use headless testing in CI/CD pipelines

### Integration Testing
- Test API routes with database integration
- Verify authentication and authorization flows
- Test form submissions and data mutations
- Check error handling and edge cases

## Deployment and Production

### Build Optimization
- Configure next.config.js for production optimizations
- Implement proper environment variable management
- Use build-time optimizations and tree shaking
- Configure custom webpack settings if needed

### Hosting Platforms
- Deploy to Vercel for optimal Next.js integration
- Consider Netlify, AWS, or other platforms
- Configure proper caching headers and CDN
- Implement proper domain and SSL configuration

### Performance Monitoring
- Use Vercel Analytics or similar for performance tracking
- Implement error tracking with Sentry or similar
- Monitor Core Web Vitals and user experience metrics
- Set up proper logging and debugging tools

## Security Best Practices

### Content Security Policy
- Implement strict CSP headers for XSS protection
- Configure proper CORS policies for API routes
- Use HTTPS and secure cookie settings
- Validate and sanitize all user inputs

### Environment Security
- Use environment variables for sensitive configuration
- Implement proper secret management
- Configure security headers in next.config.js
- Regular security audits and dependency updates

## SEO and Meta Management

### Meta Tags
- Use next/head for dynamic meta tag management
- Implement Open Graph and Twitter Card meta tags
- Use structured data for rich search results
- Configure proper canonical URLs

### Sitemap and Robots
- Generate dynamic sitemaps for SEO
- Configure robots.txt for search engine guidance
- Implement proper URL structure and redirects
- Use next-sitemap for automated sitemap generation