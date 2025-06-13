import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ExtractedData, Invoice, SaveInvoiceResponse, ModelStats } from '../models/invoice.model';

@Injectable({
  providedIn: 'root'
})
export class InvoiceService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  uploadInvoice(file: File): Observable<ExtractedData> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ExtractedData>(`${this.apiUrl}/upload-invoice/`, formData);
  }

  saveInvoice(data: { supplier: any, invoice: any, items: any[], original_extraction: any, file_path: string }): Observable<SaveInvoiceResponse> {
    return this.http.post<SaveInvoiceResponse>(`${this.apiUrl}/save-invoice/`, data);
  }

  getModelStats(): Observable<ModelStats> {
    return this.http.get<ModelStats>(`${this.apiUrl}/model-stats/`);
  }
}