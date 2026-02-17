import { Helmet } from 'react-helmet-async';
import { useLocation } from 'react-router-dom';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  type?: 'website' | 'article' | 'profile';
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
}

const SEO = ({
  title = 'A-Cube Mental Health Platform',
  description = 'Professional mental health services, therapy sessions, and wellness programs. Connect with licensed psychologists and therapists for individual and group therapy.',
  keywords = ['mental health', 'therapy', 'counseling', 'psychologist', 'wellness', 'mental wellness', 'therapy sessions', 'group therapy'],
  image = 'https://puzzle-cube-11.preview.emergentagent.com/og-image.jpg',
  type = 'website',
  author,
  publishedTime,
  modifiedTime,
}: SEOProps) => {
  const location = useLocation();
  const baseUrl = 'https://puzzle-cube-11.preview.emergentagent.com';
  const currentUrl = `${baseUrl}${location.pathname}`;

  const fullTitle = title === 'A-Cube Mental Health Platform' 
    ? title 
    : `${title} | A-Cube Mental Health Platform`;

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />
      <link rel="canonical" href={currentUrl} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content="A-Cube Mental Health Platform" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={currentUrl} />
      <meta property="twitter:title" content={fullTitle} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={image} />

      {/* Article specific tags */}
      {type === 'article' && author && (
        <meta property="article:author" content={author} />
      )}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}

      {/* Additional SEO tags */}
      <meta name="robots" content="index, follow" />
      <meta name="language" content="English" />
      <meta name="revisit-after" content="7 days" />
      <meta name="author" content="A-Cube Mental Health Platform" />
    </Helmet>
  );
};

export default SEO;
