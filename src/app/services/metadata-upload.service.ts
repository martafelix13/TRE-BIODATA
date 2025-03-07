import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MetadataUploadService {
  
  constructor( private http: HttpClient) { }
  
  private backendUrl = 'http://localhost:8080';

  submitForm(data: any, type:string) {
    data.type = type;
    return this.http.post(this.backendUrl + '/submit-form', data);
  }

  getCatalogs() {
    return this.http.get(this.backendUrl + '/catalogs');
  }

  getDatasets() {
    return this.http.get(this.backendUrl + '/datasets');
  }

  getDistributions() {
    return this.http.get(this.backendUrl + '/distributions');
  }

  getDatasetByCatalog(catalog_id: string) {
    return this.http.get(this.backendUrl + '/catalog/' + catalog_id + "/datasets");
  }

  getDistributionByDataset(dataset_id: string) {
    return this.http.get(this.backendUrl + '/dataset/' + dataset_id + "/distributions");
  }


}
