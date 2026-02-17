import { Helmet } from 'react-helmet-async';

interface StructuredDataProps {
  type: 'organization' | 'article' | 'event' | 'service';
  data: any;
}

/**
 * StructuredData component for adding JSON-LD structured data to pages
 * Helps search engines understand page content better (Phase 9.2 - SEO)
 */
const StructuredData = ({ type, data }: StructuredDataProps) => {
  const generateStructuredData = () => {
    switch (type) {
      case 'organization':
        return {
          '@context': 'https://schema.org',
          '@type': 'MedicalOrganization',
          name: data.name || 'A-Cube Mental Health Platform',
          description: data.description || 'Professional mental health services and therapy',
          url: data.url || 'https://puzzle-cube-11.preview.emergentagent.com',
          logo: data.logo || 'https://puzzle-cube-11.preview.emergentagent.com/logo.png',
          contactPoint: {
            '@type': 'ContactPoint',
            contactType: 'Customer Service',
            availableLanguage: 'English',
          },
          medicalSpecialty: 'Psychology',
          serviceType: ['Mental Health Counseling', 'Therapy Sessions', 'Group Therapy'],
        };

      case 'article':
        return {
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: data.title,
          description: data.description,
          image: data.image,
          author: {
            '@type': 'Organization',
            name: 'A-Cube Mental Health Platform',
          },
          publisher: {
            '@type': 'Organization',
            name: 'A-Cube Mental Health Platform',
            logo: {
              '@type': 'ImageObject',
              url: 'https://puzzle-cube-11.preview.emergentagent.com/logo.png',
            },
          },
          datePublished: data.publishedDate,
          dateModified: data.modifiedDate || data.publishedDate,
        };

      case 'event':
        return {
          '@context': 'https://schema.org',
          '@type': 'Event',
          name: data.title,
          description: data.description,
          startDate: data.startDate,
          endDate: data.endDate,
          location: {
            '@type': 'VirtualLocation',
            url: data.url || 'https://puzzle-cube-11.preview.emergentagent.com',
          },
          organizer: {
            '@type': 'Organization',
            name: 'A-Cube Mental Health Platform',
            url: 'https://puzzle-cube-11.preview.emergentagent.com',
          },
          eventStatus: 'https://schema.org/EventScheduled',
          eventAttendanceMode: 'https://schema.org/OnlineEventAttendanceMode',
        };

      case 'service':
        return {
          '@context': 'https://schema.org',
          '@type': 'MedicalBusiness',
          name: data.name || 'A-Cube Mental Health Platform',
          description: data.description || 'Professional therapy and counseling services',
          serviceType: data.serviceType || 'Mental Health Counseling',
          provider: {
            '@type': 'Organization',
            name: 'A-Cube Mental Health Platform',
          },
          areaServed: 'Worldwide',
          availableLanguage: 'English',
        };

      default:
        return null;
    }
  };

  const structuredData = generateStructuredData();

  if (!structuredData) return null;

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(structuredData)}
      </script>
    </Helmet>
  );
};

export default StructuredData;
