/* Example heading component, delete if not needed */

export default function Heading({ children }: { children: React.ReactNode }) {
  return <h1 className='text-3xl text-purple-400'>{children}</h1>
}
