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
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatChipsModule } from '@angular/material/chips';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { AuthService } from '../../services/auth.service';
import { RemsService } from '../../services/rems.service';


@Component({
  selector: 'app-metadata-list',
  imports: [MatCardModule, MatFormFieldModule, CommonModule, FormsModule, MatExpansionModule, MatTableModule, MatIconModule,  MatInputModule, MatListModule, MatToolbarModule, MatChipsModule],
  templateUrl: './metadata-list.component.html',
  styleUrl: './metadata-list.component.scss'
})
export class MetadataListComponent {

  datasets: any[] = [];
  filteredDatasets: any[] = [];
  distributions: any[] = [];
  searchText: string = '';
  selectedItem: any = null;
  selectedItemType: string = '';
  breadcrumbs: string[] = [];

  constructor(private metadataService: MetadataUploadService, private sanitizer: DomSanitizer, private remsService: RemsService) {}

   ngOnInit() {
      this.metadataService.getDatasets().subscribe({
        next: (data: any) => {
          this.datasets = JSON.parse(data);
          console.log("Datasets: ");
          console.log(this.datasets);
          this.filteredDatasets = this.datasets;
        },
        error: (error) => {
          console.log(error);
        }
    });
  }

  /*
  getSafeUrl(url: string): SafeUrl {
    return this.sanitizer.bypassSecurityTrustUrl(url);
  }

  filterDatasets(){
    console.log(this.searchText);
    this.filteredDatasets = this.datasets.filter(
      (dataset: { title: string; }) => dataset.title.includes(this.searchText)
    );
  }
*/
  loadDistributions(dataset: any){
    this.breadcrumbs.push(dataset.title);
    this.metadataService.getDistributionByDataset(dataset.id).subscribe({
      next: (data: any) => {
        this.distributions = JSON.parse(data);
        console.log("Distributions: ");
        console.log(this.distributions);
      },
      error: (error) => {
        console.log(error);
      }
    });
  }

  onSelectItem(item: any, type:string) {
    console.log(item);
    this.selectedItem = item;
    this.selectedItemType = type;
    if (this.selectedItemType === 'dataset') {
      this.loadDistributions(item);
    } else if ( this.selectedItemType === 'distribution') {
      this.breadcrumbs.push(item.title);
    }
  }

  onBack() {
    this.breadcrumbs.pop();
    if (this.breadcrumbs.length === 0) {
      this.selectedItem = null;
      this.selectedItemType = '';
      this.searchText = '';
      this.distributions = [];
    } else if (this.breadcrumbs.length === 1) {
      this.selectedItemType = 'dataset';
    }
  }

  redirectToRems(){
    this.remsService.redirectToRemsCatalog();
  }

}