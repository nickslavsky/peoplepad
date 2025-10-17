import { useState, useRef } from 'react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command'
import TagChip from './TagChip'

interface Props {
  suggestions: string[]
  selected?: string[]
  onChange: (tags: string[]) => void
  allowCreate?: boolean
}

export default function TagAutocomplete({
  suggestions,
  selected = [],
  onChange,
  allowCreate = true
}: Props) {
  const [open, setOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleAdd = (tag: string) => {
    if (!selected.includes(tag) && tag.trim()) {
      onChange([...selected, tag.trim()])
    }
    setInputValue('')
    // Keep focus on input after adding
    setTimeout(() => inputRef.current?.focus(), 0)
  }

  const handleRemove = (tag: string) => {
    onChange(selected.filter(t => t !== tag))
  }

  const filtered = suggestions.filter(t =>
    t.toLowerCase().includes(inputValue.toLowerCase()) && !selected.includes(t)
  )

  const showCreate = allowCreate &&
    inputValue.trim() &&
    !suggestions.some(t => t.toLowerCase() === inputValue.toLowerCase().trim())

  return (
    <Popover open={open} onOpenChange={setOpen} modal={false}>
      <PopoverTrigger asChild>
        <div
          className="flex flex-wrap items-center gap-1 border border-borderGray rounded-md p-2 cursor-text min-h-[40px]"
          onClick={() => inputRef.current?.focus()}
        >
          {selected.map(tag => (
            <TagChip key={tag} tag={tag} onRemove={() => handleRemove(tag)} />
          ))}
          <input
            ref={inputRef}
            value={inputValue}
            onChange={e => {
              setInputValue(e.target.value)
              if (!open) setOpen(true)
            }}
            onFocus={() => setOpen(true)}
            onBlur={(e) => {
              // Only close if clicking outside the popover
              if (!e.relatedTarget?.closest('[role="dialog"]')) {
                setTimeout(() => setOpen(false), 200)
              }
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && inputValue.trim()) {
                e.preventDefault()
                if (filtered.length > 0) {
                  handleAdd(filtered[0])
                } else if (showCreate) {
                  handleAdd(inputValue)
                }
              } else if (e.key === 'Escape') {
                setOpen(false)
                inputRef.current?.blur()
              }
            }}
            className="outline-none bg-transparent flex-1 min-w-[100px]"
            placeholder="Type to add tags..."
          />
        </div>
      </PopoverTrigger>
      <PopoverContent 
        className="p-0 w-[300px]" 
        align="start"
        onOpenAutoFocus={(e) => e.preventDefault()}
      >
        <Command shouldFilter={false}>
          <CommandList>
            {filtered.length === 0 && !showCreate ? (
              <CommandEmpty>No tags found.</CommandEmpty>
            ) : (
              <CommandGroup>
                {filtered.map(tag => (
                  <CommandItem
                    key={tag}
                    value={tag}
                    onSelect={() => handleAdd(tag)}
                  >
                    {tag}
                  </CommandItem>
                ))}
                {showCreate && (
                  <CommandItem
                    value={inputValue}
                    onSelect={() => handleAdd(inputValue)}
                    className="text-blue-600"
                  >
                    Create "{inputValue.trim()}"
                  </CommandItem>
                )}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}