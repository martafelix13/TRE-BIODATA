import { Component} from '@angular/core';
import { MetadataUploadService } from '../../services/metadata-upload.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule, MatFormFieldControl} from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list'

@Component({
  selector: 'app-metadata-list',
  imports: [MatCardModule, MatFormFieldModule, CommonModule, FormsModule, MatExpansionModule, MatTableModule, MatIconModule,  MatInputModule, MatListModule],
  templateUrl: './metadata-list.component.html',
  styleUrl: './metadata-list.component.scss'
})
export class MetadataListComponent {

  catalogs : any[] = [];
  filteredCatalogs: any[] = [];
  searchText: string = '';
  datasets : any[] = [];
  distributions : any[] = [];

  constructor(private metadataService: MetadataUploadService){
  }


  ngOnInit() {
      this.metadataService.getCatalogs().subscribe({
        next: (data: any) => {
          this.catalogs = JSON.parse(data);
          console.log("Catalog: ");
          console.log(this.catalogs);
          this.filteredCatalogs = this.catalogs;
          this.catalogs.map((catalog: any) => {
            this.metadataService.getDatasetByCatalog(catalog.id).subscribe({
              next: (data: any) => {
                console.log(data);
                catalog.datasets = JSON.parse(data);
              },
              error: (error) => {
                console.log(error);
              }
            });
          });
        },
        error: (error) => {
          console.log(error);
        }
      })
  }

  loadDistributions(dataset: any){
    this.metadataService.getDatasetByCatalog(dataset.id).subscribe({
      next: (data: any) => {
        console.log(data);
        dataset.distributions = JSON.parse(data);
      },
      error: (error) => {
        console.log(error);
      }
    });
  }

  filterCatalogs(){
    this.filteredCatalogs = this.catalogs.filter(
      (catalog: { title: string; }) => catalog.title.includes(this.searchText)
    );
  }
}