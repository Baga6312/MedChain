import { CalendarDays, FileHeart, Stethoscope, UserRound } from 'lucide-react';

// field.ref -> foreign key to another resource (rendered as a select)
// field.nullable -> empty string is sent as null
export const resources = {
  doctors: {
    label: 'Médecins',
    singular: 'médecin',
    icon: Stethoscope,
    fields: [
      { name: 'name', label: 'Nom', type: 'text' },
      { name: 'specialty', label: 'Spécialité', type: 'text' },
    ],
  },
  patients: {
    label: 'Patients',
    singular: 'patient',
    icon: UserRound,
    fields: [
      { name: 'name', label: 'Nom', type: 'text' },
      { name: 'birth_date', label: 'Date de naissance', type: 'date', nullable: true },
      { name: 'phone', label: 'Téléphone', type: 'text' },
    ],
  },
  appointments: {
    label: 'Rendez-vous',
    singular: 'rendez-vous',
    icon: CalendarDays,
    fields: [
      { name: 'patient', label: 'Patient', ref: 'patients' },
      { name: 'doctor', label: 'Médecin', ref: 'doctors' },
      { name: 'date', label: 'Date', type: 'datetime-local' },
      { name: 'notes', label: 'Notes', type: 'textarea' },
      // TODO: replace with a select once Appointment.Status values are known
      { name: 'status', label: 'Statut', type: 'text' },
    ],
  },
  'medical-records': {
    label: 'Dossiers médicaux',
    singular: 'dossier',
    icon: FileHeart,
    fields: [
      { name: 'patient', label: 'Patient', ref: 'patients' },
      { name: 'title', label: 'Titre', type: 'text' },
      { name: 'content', label: 'Contenu', type: 'textarea' },
    ],
  },
};