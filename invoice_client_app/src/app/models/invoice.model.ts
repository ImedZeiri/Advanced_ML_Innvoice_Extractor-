export interface Supplier {
  id?: number;
  name: string;
  siret?: string;
  address?: string;
  created_at?: string;
  updated_at?: string;
}

export interface InvoiceItem {
  id?: number;
  invoice: number;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  tax_rate: number;
}

export interface Invoice {
  id?: number;
  file: string;
  original_filename: string;
  status: 'pending' | 'processing' | 'processed' | 'error' | 'validated';
  supplier?: number;
  supplier_name?: string;
  invoice_number?: string;
  invoice_date?: string;
  due_date?: string;
  total_amount?: number;
  tax_amount?: number;
  confidence_score: number;
  created_at?: string;
  updated_at?: string;
  items?: InvoiceItem[];
}

export interface ExtractedData {
  invoice_number?: string;
  invoice_date?: string;
  total_amount?: number;
  tax_amount?: number;
  supplier_name?: string;
  confidence_score: number;
}

export interface UploadResponse {
  invoice: Invoice;
  extracted_text: string;
  extracted_data: ExtractedData;
}