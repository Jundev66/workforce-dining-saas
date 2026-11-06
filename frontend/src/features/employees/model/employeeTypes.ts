import { SyncStatus } from '../../../shared/offline/syncLedger';

export interface Employee {
  id: string;
  tenant_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  document_id: string;
  department: string;
  position: string;
  status: 'active' | 'inactive' | 'on_leave';
  badge_code: string;
  email?: string | null;
  phone?: string | null;
  created_at?: string;
  updated_at?: string;
  // Offline sync & audit metadata
  sync_status?: SyncStatus;
  sync_error?: string | null;
  sync_transaction_id?: string;
}

export interface PaginatedEmployees {
  items: Employee[];
  total: number;
  skip: number;
  limit: number;
}
