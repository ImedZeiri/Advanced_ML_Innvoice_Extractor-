import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { InvoiceService } from '../../services/invoice.service';
import { UploadResponse } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-upload',
  templateUrl: './invoice-upload.component.html',
  styleUrls: ['./invoice-upload.component.scss']
})
export class InvoiceUploadComponent implements OnInit {
  selectedFile: File | null = null;
  isUploading = false;
  uploadProgress = 0;
  uploadResponse: UploadResponse | null = null;

  constructor(
    private invoiceService: InvoiceService,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
  }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0] as File;
  }

  uploadInvoice(): void {
    if (!this.selectedFile) {
      this.snackBar.open('Veuillez sélectionner un fichier', 'Fermer', {
        duration: 3000
      });
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;

    // Simulation de la progression
    const interval = setInterval(() => {
      this.uploadProgress += 10;
      if (this.uploadProgress >= 90) {
        clearInterval(interval);
      }
    }, 300);

    this.invoiceService.uploadInvoice(this.selectedFile).subscribe({
      next: (response) => {
        this.uploadProgress = 100;
        this.uploadResponse = response;
        this.isUploading = false;
        clearInterval(interval);
        
        this.snackBar.open('Facture téléchargée avec succès', 'Fermer', {
          duration: 3000
        });
      },
      error: (error) => {
        this.isUploading = false;
        clearInterval(interval);
        
        this.snackBar.open('Erreur lors du téléchargement de la facture', 'Fermer', {
          duration: 3000
        });
        console.error('Erreur lors du téléchargement:', error);
      }
    });
  }

  viewInvoice(): void {
    if (this.uploadResponse && this.uploadResponse.invoice.id) {
      this.router.navigate(['/invoices', this.uploadResponse.invoice.id]);
    }
  }

  editInvoice(): void {
    if (this.uploadResponse && this.uploadResponse.invoice.id) {
      this.router.navigate(['/invoices', this.uploadResponse.invoice.id, 'edit']);
    }
  }
}