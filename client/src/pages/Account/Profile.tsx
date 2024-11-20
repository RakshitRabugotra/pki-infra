import Heading from '@/components/Heading'

// Custom Hooks
import { useTitle } from '@/utils/hooks'

export default function Profile() {
  // Set the title of the page
  useTitle('Profile')

  return <Heading>Profile Page</Heading>
}
