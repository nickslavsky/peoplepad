import { useQuery } from '@tanstack/react-query'
import { getTags } from '@/lib/api'

export const useTags = () => useQuery({
  queryKey: ['tags'],
  queryFn: getTags,
})