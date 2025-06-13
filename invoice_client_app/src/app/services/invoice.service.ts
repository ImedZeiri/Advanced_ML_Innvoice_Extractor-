import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Invoice, UploadResponse, ExtractedData } from '../models/invoice.model';

@Injectable({
  providedIn: 'root'
})
export class InvoiceService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // Récupérer toutes les factures
  getInvoices(): Observable<Invoice[]> {
    return this.http.get<Invoice[]>(`${this.apiUrl}/invoices/`);
  }

  // Récupérer une facture par son ID
  getInvoice(id: number): Observable<Invoice> {
    return this.http.get<Invoice>(`${this.apiUrl}/invoices/${id}/`);
  }

  // Uploader une nouvelle facture
  uploadInvoice(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<UploadResponse>(`${this.apiUrl}/invoices/upload/`, formData);
  }

  // Valider et corriger les données extraites
  validateInvoice(id: number, correctedData: ExtractedData): Observable<any> {
    return this.http.post(`${this.apiUrl}/invoices/${id}/validate/`, { corrected_data: correctedData });
  }

  // Entraîner le modèle ML
  trainModel(): Observable<any> {
    return this.http.post(`${this.apiUrl}/train-model/`, {});
  }
}