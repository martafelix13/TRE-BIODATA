import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { SanityChecks } from '@angular/material/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MetadataUploadService {
  
  constructor( private http: HttpClient) { }
  
  private backendUrl = environment.serverUrl;

  submitForm(data: any, type:string) {
    data.type = type;
    return this.http.post(this.backendUrl + '/submit-form', data);
  }

  submitDataset(data: any) {
    return this.http.post(this.backendUrl + '/fdp/upload-dataset', data)
  }

  submitCatalog(data:any){
    return this.http.post(this.backendUrl + '/fdp/upload-catalog', data)
  }

  getCatalogs() {
    return this.http.get(this.backendUrl + '/fdp/catalogs');
  }

  getDatasets() {
    return this.http.get(this.backendUrl + '/fdp/datasets');
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
