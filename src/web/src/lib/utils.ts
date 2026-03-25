import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Combina classi Tailwind con merge intelligente */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Formatta un numero come valuta (€) */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}

/** Formatta una data in formato italiano */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(date))
}

/** Formatta misure mm → cm con 1 decimale */
export function formatMeasure(mm: number): string {
  return (mm / 10).toFixed(1)
}

/** Formatta area mm² → m² con 2 decimali */
export function formatArea(widthMm: number, heightMm: number): string {
  return ((widthMm * heightMm) / 1_000_000).toFixed(2)
}
