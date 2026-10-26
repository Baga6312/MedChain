import { Navigate, useParams } from 'react-router-dom';
import CrudPage from '../components/crud/crudPage';
import { resources } from '../config/resources';
import { useNotify } from '../context/NotifyContext';

export default function ResourcePage() {
  const { resource } = useParams();
  const notify = useNotify();
  if (!resources[resource]) return <Navigate to="/patients" replace />;
  return <CrudPage key={resource} resource={resource} notify={notify} />;
}