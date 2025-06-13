import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { InvoiceService } from '../../services/invoice.service';
import { Invoice, ExtractedData } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-edit',
  templateUrl: './invoice-edit.component.html',
  styleUrls: ['./invoice-edit.component.scss']
})
export class InvoiceEditComponent implements OnInit {
  invoiceId!: number;
  invoice: Invoice | null = null;
  invoiceForm!: FormGroup;
  isLoading = true;
  isSaving = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private invoiceService: InvoiceService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.invoiceId = +this.route.snapshot.paramMap.get('id')!;
    this.createForm();
    this.loadInvoice();
  }

  createForm(): void {
    this.invoiceForm = this.fb.group({
      invoice_number: ['', Validators.required],
      invoice_date: [''],
      supplier_name: ['', Validators.required],
      total_amount: [0, [Validators.required, Validators.min(0)]],
      tax_amount: [0, [Validators.min(0)]]
    });
  }

  loadInvoice(): void {
    this.isLoading = true;
    this.invoiceService.getInvoice(this.invoiceId).subscribe({
      next: (invoice) => {
        this.invoice = invoice;
        this.updateForm();
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBar.open('Erreur lors du chargement de la facture', 'Fermer', {
          duration: 3000
        });
        this.isLoading = false;
        console.error('Erreur lors du chargement:', error);
      }
    });
  }

  updateForm(): void {
    if (this.invoice) {
      this.invoiceForm.patchValue({
        invoice_number: this.invoice.invoice_number || '',
        invoice_date: this.invoice.invoice_date || '',
        supplier_name: this.invoice.supplier_name || '',
        total_amount: this.invoice.total_amount || 0,
        tax_amount: this.invoice.tax_amount || 0
      });
    }
  }

  saveChanges(): void {
    if (this.invoiceForm.invalid) {
      this.snackBar.open('Veuillez corriger les erreurs du formulaire', 'Fermer', {
        duration: 3000
      });
      return;
    }

    this.isSaving = true;
    const correctedData: ExtractedData = {
      invoice_number: this.invoiceForm.value.invoice_number,
      invoice_date: this.invoiceForm.value.invoice_date,
      supplier_name: this.invoiceForm.value.supplier_name,
      total_amount: this.invoiceForm.value.total_amount,
      tax_amount: this.invoiceForm.value.tax_amount,
      confidence_score: 1.0 // Score de confiance maximum car validé manuellement
    };

    this.invoiceService.validateInvoice(this.invoiceId, correctedData).subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open('Facture mise à jour avec succès', 'Fermer', {
          duration: 3000
        });
        this.router.navigate(['/invoices', this.invoiceId]);
      },
      error: (error) => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de la mise à jour de la facture', 'Fermer', {
          duration: 3000
        });
        console.error('Erreur lors de la mise à jour:', error);
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/invoices', this.invoiceId]);
  }
}