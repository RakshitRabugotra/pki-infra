import Heading from '@/components/Heading'

// Custom Hooks
import { useTitle } from '@/utils/hooks'

export default function ProfileSettings() {
  // Set the title of the page
  useTitle('Settings')

  return <Heading>Profile Settings</Heading>
}
