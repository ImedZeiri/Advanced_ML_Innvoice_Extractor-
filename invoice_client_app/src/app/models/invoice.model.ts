export interface Supplier {
  name: string;
  address: string;
  tax_id: string;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  tax_rate: number;
}

export interface Invoice {
  invoice_number: string;
  date: string;
  due_date?: string;
  supplier: Supplier;
  total_amount: number;
  tax_amount: number;
  items: InvoiceItem[];
}

export interface ExtractedData {
  status: string;
  extracted_data: Invoice;
  original_text: string;
}

export interface SaveInvoiceResponse {
  status: string;
  message: string;
  invoice_id: number;
}

export interface ModelStats {
  status: string;
  active_model: {
    name: string;
    version: string;
    accuracy: number;
    created_at: string;
  } | null;
  total_invoices: number;
  training_data_count: number;
  used_for_training: number;
  pending_training: number;
}