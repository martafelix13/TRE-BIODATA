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

  uploadMetadata(dataset: any, distributions: any[]) {
    const data = {
      dataset: dataset,
      distributions: distributions
    };
    return this.http.post(this.backendUrl + '/fdp/upload', data, { withCredentials: true });
  }

  getCatalogs() {
    return this.http.get(this.backendUrl + '/fdp/catalogs', { withCredentials: true });
  }

  getDatasets() {
    return this.http.get(this.backendUrl + '/fdp/datasets', { withCredentials: true });
  }

  getDistributions() {
    return this.http.get(this.backendUrl + '/distributions', { withCredentials: true });
  }

  getDatasetByCatalog(catalog_id: string) {
    return this.http.get(this.backendUrl + '/catalog/' + catalog_id + "/datasets", { withCredentials: true });
  }

  getDistributionByDataset(dataset_id: string) {
    return this.http.get(this.backendUrl + '/dataset/' + dataset_id + "/distributions", { withCredentials: true });
  }

  fetchSkosLabel(uri: string)  { 
    return this.http.get(this.backendUrl + '/skos/label?uri=' + uri, { withCredentials: true });
  }

  getContactInfo(uri: string) {
    return this.http.get(this.backendUrl + '/contact-info?uri=' + uri, { withCredentials: true });
  }

}
