// Administrador del Mercado Mayorista
// Librera de Funciones - Portal Web - Informes
// Elaborado por: Carlos Berges
// Diciembre 2011
// Modificaciones: Alexander Godínez
// Diciembre 2025
// Modificaciones: Rubén Rojas
function abrirVentana(url) {
	window.open(url, "nuevo", "directories=no, location=no, menubar=no, scrollbars=yes, statusbar=no, tittlebar=no, width=400, height=400");
}

function llenaInformes(tipo_emision) {
	
	if (tipo_emision == 'diario') {
		$("#informes").append('<option value=dia_postdespacho>Posdespacho</option>');
		$("#informes").append('<option value=dia_posdes_reg>Posdespacho Regional</option>');
		$("#informes").append('<option value=dia_infeveser>Desconexi&oacute;n Autom&aacute;tica por Baja Frecuencia</option>');
	} else if (tipo_emision == 'diario_pla') {
		$("#informes").append('<option value=dia_despacho>Despacho Diario</option>');
	} else if (tipo_emision == 'semanal') {
		$("#informes").append('<option value=sem_spot_horario>Datos del Precio SPOT Horario</option>');
		$("#informes").append('<option value=ano_post_operativo>Informe Post-operativo</option>');
	} else if (tipo_emision == 'semanal_pla') {
		$("#informes").append('<option value=sem_despacho>Despacho Semanal</option>');
		$("#informes").append('<option value=sem_rep_mant_pre>Reporte Preliminar de Mantenimientos</option>');
		$("#informes").append('<option value=sem_rep_mant_def>Reporte Definitivo de Mantenimientos</option>');
	} else if (tipo_emision == 'mensual') {
		$("#informes").append('<option value=mes_spot_promedio>Grafico Precio SPOT Promedio</option>');
		$("#informes").append('<option value=mes_ite>Informe de Transacciones Economicas</option>');
		$("#informes").append('<option value=mes_postdespacho>PosDespacho Mensual</option>');
		$("#informes").append('<option value=mes_listaagentes>Agentes Habilitados</option>'); 
		//$("#informes").append('<option value=mes_ageninhab>Agentes y Grandes Usuarios Inhabilitados</option>');
	} else if (tipo_emision == 'trimensual') {
		$("#informes").append('<option value=trimes_programacion>Programaci&oacute;n Trimestral</option>');
	} else if (tipo_emision == 'mensual_pla') {
		$("#informes").append('<option value=mes_plp>Programaci&oacute;n Mensual</option>');
	} else if (tipo_emision == 'anual') {
		$("#informes").append('<option value=ano_cap_inst>Capacidad Instalada</option>');
		$("#informes").append('<option value=ano_demanda_firme>Demanda Firme de Consumidores</option>');
		$("#informes").append('<option value=ano_generacion_pdf>Generacion Mensual por Planta (PDF)</option>');
		$("#informes").append('<option value=ano_generacion_xls>Generacion Mensual por Planta (XLS)</option>');
		$("#informes").append('<option value=ano_estadistico_anual>Informe Estad&iacute;stico Anual</option>');
		$("#informes").append('<option value=ano_memoria_labores>Memoria de Labores</option>');
		$("#informes").append('<option value=ano_oferta_firme>Oferta Firme Eficiente</option>');
		$("#informes").append('<option value=ano_spot_anual>Precios SPOT Anuales</option>');
	} else if (tipo_emision == 'anual_pla') {
		$("#informes").append('<option value=ano_despacho_estacional>Despacho Estacional (PLP)</option>');
	} else if (tipo_emision == 'mer') {
		$("#informes").append('<option value=cdiariatiemporeal>Conciliaci&oacute;n Diaria En tiempo Real</option>');
		$("#informes").append('<option value=cdiariaprog>Conciliaci&oacute;n Diaria Programada</option>');
		$("#informes").append('<option value=mes_dter>DTER</option>');
		$("#informes").append('<option value=dia_posdes>PosDespacho Regional</option>');
		$("#informes").append('<option value=dia_concrie50>Conciliación de Transacciones CRIE-50-2020</option>');
	} else if (tipo_emision == 'mer_pla') {
		$("#informes").append('<option value=dia_predes>PreDespacho Regional</option>');
		$("#informes").append('<option value=dia_predescrie50>Predespacho Regional CRIE-50-2020</option>');
		
	}
}

function llenaInformesSemanal(seleccionado) {
	var selPre='';
	var selDef='';
	var selSem='';
	//alert('valor seleccionado II:'+seleccionado);
	if (seleccionado =='sem_rep_mant_pre')
		selPre=' selected ';
	if (seleccionado =='sem_rep_mant_def')
		selDef=' selected ';
	if (seleccionado =='sem_despacho')
		selSem=' selected ';

	$("#informes").append('<option value=sem_spot_horario>Datos del Precio SPOT Horario</option>');
	//$("#informes").append('<option value=ano_post_operativo>Informe Post-operativo</option>');
	//$("#informes").append('<option value="sem_resum_grafico">Resumen Gr&aacute;fico del Mercado Mayorista</option>');

}

function llenaInformesSemanal_plani(seleccionado) {
	var selPre='';
	var selDef='';
	var selSem='';
	//alert('valor seleccionado II:'+seleccionado);
	//$("#informes").append('<option value=sem_despacho>Despacho Semanal</option>');
	//	$("#informes").append('<option value=sem_rep_mant_pre>Reporte Preliminar de Mantenimientos</option>');
	//	$("#informes").append('<option value=sem_rep_mant_def>Reporte Definitivo de Mantenimientos</option>');
	
	if (seleccionado =='sem_rep_mant_pre')
		selPre=' selected ';
	if (seleccionado =='sem_rep_mant_def')
		selDef=' selected ';
	if (seleccionado =='sem_despacho')
		selSem=' selected ';

	$("#informes").append('<option value="sem_despacho" ' + selSem + '>Despacho Semanal</option>');
	$("#informes").append('<option value="sem_rep_mant_pre" ' + selPre + '>Reporte Preliminar de Mantenimientos</option>');
	$("#informes").append('<option value="sem_rep_mant_def" ' + selDef + '>Reporte Definitivo de Mantenimientos</option>');

}

function visualizaDocumento() {
	// Diego Rivas
 	// 13032019 Modificación a HTTPS por Implementación de Certificado
        // var direccion01= 'http://www.amm.org.gt/';
	var direccion01= 'https://www.amm.org.gt/';
	//var direccion01= 'http://192.9.200.6/';
	var direccion02 = '';
	var carpeta_padre='';

	var mes_largo=['','ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'];
	
	// Obtiene Dia, Mes y Ao por Separado
	var fecha_sel = $("#fecha_seleccionada").val();
	//fecha de programas semanales
	var fecha_sel_sem = $("#cal_mensual").val();
	//anio seleccionado de docs anuales
	var fecha_sel_an = $("#anio_seleccionado").val();
	
	//alert('fecha_sel:'+fecha_sel+' fecha_sel_sem:'+fecha_sel_sem+' fecha_sel_an:'+fecha_sel_an);
	
	if (fecha_sel.length==0 && (fecha_sel_an==null || fecha_sel_an.length==0)) {
		fecha_sel='01/'+fecha_sel_sem;
	} else if (fecha_sel.length==0 && (fecha_sel_sem==null || fecha_sel_sem.length==0)) {
		fecha_sel='01/01/'+fecha_sel_an;
	}

	var dia = fecha_sel.substr(0,2);
	var mes  = fecha_sel.substr(3,2);
	var anio = fecha_sel.substr(6,4);
	var fecha_txt = anio + mes + dia + '';
	var anio2d = anio.substr(2,2);
	var anio_int = parseInt(anio2d);
	var anio_sig = anio_int + 1;
	var anio4dint = parseInt(anio);
	var mesint = parseInt(mes,10);

	
	var fechaJS = new Date(anio, mes-1, dia);

	var botonindice=0;
	var resp_verifica_fecha=true;

	if ($("#informes").val() == 'sem_rep_mant_pre' || $("#informes").val()=='sem_rep_mant_def') { 
		resp_verifica_fecha=true;
	} else {
		//resp_verifica_fecha=verificaFecha(fechaJS); // para impedir que se seleccione una fecha mayor a hoy
		resp_verifica_fecha=true; 
	}

	var mostrarVentana=true;
	if (resp_verifica_fecha) {  // modificacion Alex Godinez
		var carpeta_pdfs='pdfs2';  // AGS
	
		var semanaint = fechaJS.getWeekOfYear();
		//alert('semana: '+semanaint);
		//numeroSemana(dia,mes-1,anio);
		var ultimo_domingo = ultimoDomingo(fechaJS);
		var ultimo_domingo_dd = ultimo_domingo.getDate(); if (ultimo_domingo_dd < 10) {ultimo_domingo_dd = '0' + ultimo_domingo_dd;}
		var ultimo_domingo_mm = ultimo_domingo.getMonth()+1; if (ultimo_domingo_mm < 10) {ultimo_domingo_mm = '0' + ultimo_domingo_mm;}
		var ultimo_domingo_aa = ultimo_domingo.getFullYear();
		var fecha_ultimo_domingo = ultimo_domingo_aa + '' +  ultimo_domingo_mm + '' + ultimo_domingo_dd;
	
		// Obtiene nombre del mes
		var mes_txt = '';
		if (mes == '01') {mes_txt = 'ene'} else if (mes == '02') {mes_txt = 'feb'} else if (mes == '03') {mes_txt = 'mar'} else if (mes == '04') {mes_txt = 'abr'}
		else if (mes == '05') {mes_txt = 'may'} else if (mes == '06') {mes_txt = 'jun'} else if (mes == '07') {mes_txt = 'jul'} else if (mes == '08') {mes_txt = 'ago'}
		else if (mes == '09') {mes_txt = 'sep'} else if (mes == '10') {mes_txt = 'oct'} else if (mes == '11') {mes_txt = 'nov'} else if (mes == '12') {mes_txt = 'dic'}

		
		
		// ********************************
		//     _ _          _        
		//  __| (_)__ _ _ _(_)___ ___
		// / _` | / _` | '_| / _ (_-<
		// \__,_|_\__,_|_| |_\___/__/
		//
		//*********************************

		if ($("#informes").val() == 'dia_despacho') { 
			botonindice=1; 
			var extension='.html';
			if ((mesint<8 && anio4dint==2007) || anio4dint<=2006) {
				extension='.pdf';
			}
			
			if ((mesint<7 && anio4dint==2001) || anio4dint<=2000) {
				mostrarVentana=false;
				alert('No existen Informes de Despacho para la fecha seleccionada');
			} else if (anio4dint>=2012) {
				botonindice=0; 
				extension='.xls';
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'pd.php?fecha='+dia+mes+anio+'&mes='+mesint+'&anio=' + anio;
			} else {
				direccion02 = carpeta_pdfs + '/' + anio + '/despacho/' + mes_txt + '/PDD' + fecha_txt + '_01' + extension; 
			} 
		}

		if ($("#informes").val() == 'dia_postdespacho') { 
			botonindice=1; 
			var extension='.html';
			var nombre_pd='INFP' + fecha_txt + '_01';
			if ((mesint<7 && anio4dint==2007) || anio4dint<=2006) {
				nombre_pd+='.pdf';
				direccion02 = carpeta_pdfs + '/' + anio + '/posdespacho/' + mes_txt + '/' + nombre_pd; 
			} else if (mesint>=8 && anio4dint>=2012) { // para la carpeta nueva
				botonindice=0; 
				nombre_pd='PD'+ fecha_txt + '.zip';
				direccion02 = carpeta_pdfs + '/post_despacho/POSDESPACHO_DIARIO/' + anio + "/" + mes + '_' + mes_largo[mesint] + '/' + nombre_pd; 
			} else if (anio4dint>=2013) { // para la carpeta nueva
				botonindice=0; 
				nombre_pd='PD'+ fecha_txt + '.zip';
				direccion02 = carpeta_pdfs + '/post_despacho/POSDESPACHO_DIARIO/' + anio + "/" + mes + '_' + mes_largo[mesint] + '/' + nombre_pd; 
			} else {
				nombre_pd+='.html';
				direccion02 = carpeta_pdfs + '/' + anio + '/posdespacho/' + mes_txt + '/' + nombre_pd; 
			}
			if (anio4dint<2002) {
				mostrarVentana=false;
				alert('No existen Informes de PostDespacho para la fecha seleccionada');
			}

			//direccion02 = carpeta_pdfs + '/' + anio + '/posdespacho/' + mes_txt + '/INFP' + fecha_txt + '_01' + extension; 
		}
		
		if ($("#informes").val() == 'dia_posdes_reg') {
			var nombre_pd='PDR'+ fecha_txt + '.zip';
			if ((mesint<11 && anio4dint<=2013) || anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de PosDespacho Regional para la fecha seleccionada');
			} else {
				direccion02 = carpeta_pdfs + '/post_despacho/POSDESPACHO_DIARIO_REGIONAL/' + anio + "/" + mes + '_' + mes_largo[mesint] + '/' + nombre_pd; 
			} 
		}
		
		if ($("#informes").val() == 'dia_infeveser') { 
			botonindice=1; 
			
			if ((mesint<3 && anio4dint==2022) || anio4dint<=2021) {
				mostrarVentana=false;
				alert('No existen Informes de Eventos para la fecha seleccionada');
			} else if (anio4dint>=2022) {
				botonindice=0; 
				direccion02 = '/'+carpeta_padre+'infeveser.php?fecha='+anio2d+mes+dia+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		//-------------------------------------
		//  ._._ _ _|_ _._ _._|_ _ 
		//  |_| (/(_(/_>|_(_(_| (_)
		//  |           |
		//-------------------------------------
		if ($("#informes").val() == 'dia_predes_indi') { 
			botonindice=0; 
			direccion02 = '/'+carpeta_padre+'predes_indi.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
		}
		
		if ($("#informes").val() == 'dia_predes') {
			if (mesint<6 && anio4dint<=2013) {
				mostrarVentana=false;
				alert('No existen Informes de PreDespacho para la fecha seleccionada');
			} else {
				botonindice=0; 
				direccion02 = '/'+carpeta_padre+'predes.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			}
			
		}
		
		//-------------------------------------
		//  ._ _ _ _|_ _._ _._|_ _ 
		//  |_(__>(_(/_>|_(_(_| (_)
		//  |           |
		//-------------------------------------
		if ($("#informes").val() == 'dia_posdes_indi') { 
			botonindice=0;
			direccion02 = '/'+carpeta_padre+'posdes_indi.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
		}
		
		if ($("#informes").val() == 'dia_posdes') {
			if (mesint<6 && anio4dint<=2013) {
				mostrarVentana=false;
				alert('No existen Informes de PreDespacho para la fecha seleccionada');
			} else {
				botonindice=0;
				direccion02 = '/'+carpeta_padre+'posdes.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			}
		}
		
		//   ___ ___ ___ ___   ___  __    ___ __ ___ __  
		//  / __| _ \_ _| __| | __|/  \  |_  )  \_  )  \ 
		// | (__|   /| || _|  |__ \ () |  / / () / / () |
		//  \___|_|_\___|___| |___/\__/  /___\__/___\__/
		//dia_predescrie50 dia_concrie50
		if ($("#informes").val() == 'dia_predescrie50') {
			if (dia<25 && mesint<=9 && anio4dint<=2020) {
				mostrarVentana=false;
				alert('No existen Informes de Despachos para la fecha seleccionada');
			} else {
				botonindice=0;
				direccion02 = '/'+carpeta_padre+'crie50pre.php?fecha='+anio+mes+dia+'&mes='+mesint+'&dia='+dia+'&anio=' + anio;
			}
		}
		
		if ($("#informes").val() == 'dia_concrie50') {
			if (dia<25 && mesint<=9 && anio4dint<=2020) {
				mostrarVentana=false;
				alert('No existen Informes de Conciliación para la fecha seleccionada');
			} else {
				botonindice=0;
				direccion02 = '/'+carpeta_padre+'crie50con.php?fecha='+anio+mes+dia+'&mes='+mesint+'&dia='+dia+'&anio=' + anio;
			}
		}
		
		

		//********************************************
		//                               _        
		//  ___ ___ _ __  __ _ _ _  __ _| |___ ___
		// (_-</ -_) '  \/ _` | ' \/ _` | / -_|_-<
		// /__/\___|_|_|_\__,_|_||_\__,_|_\___/__/
		//********************************************
		
		//validacion del numero de semana ultimo
		var diaultimodomingo = parseInt(ultimo_domingo_dd,10);
		var mesultimodomingo = parseInt(ultimo_domingo_mm,10);
		//if (diaultimodomingo>28 && diaultimodomingo<=31) {
		//if (diaultimodomingo>=28 && mesint==12) {
		if (diaultimodomingo>=28 && mesultimodomingo==12) { // AGS 26122013 para que tome la semana correcta
			semanaint=1;
			aniofecha=fecha_ultimo_domingo.substr(0,4);
			anio4dint=parseInt(aniofecha,10)+1;
			anio=''+anio4dint;
		} else if (anio4dint==2013) { //bug que no toma la primera semana como 1era sino como 53 del anio anterior
			if (semanaint==53)
				semanaint=1;
			else
				semanaint++;
		} else if (anio4dint==2014) { //correccion de bug
			semanaint++;
		} else if (anio4dint==2015) { //correccion de bug
			semanaint++;
		} else if (anio4dint==2016) { //correccion de bug
			if (mesint==1 && (dia==1 || dia==2)) {
				semanaint++;
				anio='2015';
			} else
				semanaint=semanaint;
		} else if (anio4dint==2018) { //correccion de bug
			// if (mesint==1 || mesint==2 && (dia>=1 || dia<=6)) {
			if ((dia>=1 || dia<=6)) {

				semanaint++;
				anio='2018';
			} else
				semanaint=semanaint;
		} else if (anio4dint==2019) {
			semanaint++;
		} else if (anio4dint==2020) {
			semanaint++;
		} else if (anio4dint==2024) {
			if (dia<7 && mesint==1)
				semanaint = semanaint;
			else
				semanaint++;
		} else if (anio4dint==2025) {
			if (dia<5 && mesint==1)
				semanaint = semanaint;
			else
				semanaint++;
		} else if (anio4dint==2026) {
			if (dia<4 && mesint==1)
				semanaint = semanaint;
			else
				semanaint++;
  		}


               //if (anio4dint == 2025 && semanaint == 1 && mesint == 12 ) {
                 //     anio4dint = 2024;                      
                 //     console.log("Entro..."); 
               //}
                console.log(anio4dint)
                console.log(mesint)
                console.log(dia)
		console.log(semanaint)

		var semana = '';
		if (semanaint<10)
			semana = '0' + semanaint;
		else
			semana = '' + semanaint;
			
		//console.log('semana '+semana);

		if ($("#informes").val() == 'sem_spot_horario') { 
			var extension='.xls';
			var carpeta_anio=anio;
			if (anio=='2001' || anio=='2002')
				extension='.pdf';
			if (anio!=ultimo_domingo_aa)
				carpeta_anio=ultimo_domingo_aa;
			if (anio4dint<2001) {
				mostrarVentana=false;
				alert('No existen Informes del Precio SPOT Horario para la fecha seleccionada');
			}

                        var mesesRestar = 1;
			var diasHabilesITE = 13;
			var fechaActual = new Date();			
			var anioActual = fechaActual.getFullYear();
			var mesActual = parseInt(fechaActual.getMonth()) + 1;												
			var diasHabiles = 0;									
			for(var i = 0; i < 25; i++) {
				var fechaI = new Date(anioActual, mesActual - 1, i + 1);
				if (fechaI.getDay() != 0 && fechaI.getDay() != 6) {
					diasHabiles++;
					if (diasHabiles == diasHabilesITE) {
						if (fechaActual < fechaI) {	
   						    mesesRestar++;					
						}						
						break;
					}
				}			
			}							
			var fechaTest = fechaJS;
			var anioTest = fechaTest.getFullYear();
			var mesTest = parseInt(fechaTest.getMonth()) + 1;			
			var ultimoITE = (anioActual * 12) + mesActual - mesesRestar;		
			var ultimoFechaTest = (anioTest * 12) + mesTest;					
			var result = (ultimoITE >= ultimoFechaTest);
			if (!result) {
                            mostrarVentana=false;
                            alert('Solamente existen datos hasta la fecha correspondiente al Ultimo ITE Version Original publicado');   
                        }
			direccion02 = carpeta_pdfs + '/' + carpeta_anio + '/spot/PSS' + fecha_ultimo_domingo + extension; 
		} 
		
		if ($("#informes").val() == 'sem_despacho') { 
			if (anio4dint<2002) {
				mostrarVentana=false;
				alert('No existen Informes de Despacho Semanal para la fecha seleccionada');
			}

			if (anio4dint>=2012) {
				//direccion02 = carpeta_pdfs + '/programas_despacho/02_PROGRAMAS_DE_DESPACHO_SEMANAL/' + anio + '/01_PROGRAMAS_DE_DESPACHO_SEMANAL/' + semana + '_PDS' + fecha_ultimo_domingo + '.xls'; 
				direccion02 = '/'+carpeta_padre+'pds.php?anio=' + anio + '&fechadomingo=' + fecha_ultimo_domingo + '&semana=' + semana;
			} else {
				direccion02 = carpeta_pdfs + '/' + anio + '/prog_despacho/PDS' + fecha_ultimo_domingo + '.pdf';
			}
		}
			
		if ($("#informes").val() == 'ano_post_operativo') { 
			if ((dia<24 && mes<=6 && anio4dint==2007) || anio4dint<2007) {
				mostrarVentana=false;
				alert('No existen Informes Post-Operativo para la fecha seleccionada');
			}
			direccion02 = carpeta_pdfs + '/' + anio + '/ipo/IPO' + fecha_ultimo_domingo + '.pdf'; 
		}

		if ($("#informes").val() == 'sem_rep_mant_pre') { 
			if (anio4dint<2012) {
				mostrarVentana=false;
				alert('No existen Informes de Mantenimientos Preliminares');
			}
			//direccion02 = carpeta_pdfs + '/programas_despacho/04_REPORTE_DE_MANTENIMIENTOS/' + anio + '/01_REPORTE_PRELIMINAR_DE_MANTENIMIENTOS/';
			//direccion02 += semana + '_REPMANT' + fecha_ultimo_domingo + '_VP.xls';
			//console.log('semana '+semana+ ' f '+fecha_ultimo_domingo+' a '+anio);
			direccion02 = '/'+carpeta_padre+'repmantpre.php?anio=' + anio + '&fechadomingo=' + fecha_ultimo_domingo + '&semana=' + semana;
		}

		if ($("#informes").val() == 'sem_rep_mant_def') { 
			if (anio4dint<2012) {
				mostrarVentana=false;
				alert('No existen Informes de Mantenimientos Definitivos');
			}
			//direccion02 = carpeta_pdfs + '/programas_despacho/04_REPORTE_DE_MANTENIMIENTOS/' + anio + '/02_REPORTE_DEFINITIVO_DE_MANTENIMIENTOS/';
			//direccion02 += semana + '_REPMANT' + fecha_ultimo_domingo + '_VD.xls';
			direccion02 = '/'+carpeta_padre+'repmantdef.php?anio=' + anio + '&fechadomingo=' + fecha_ultimo_domingo + '&semana=' + semana;
		}
			
		// RESUMEN GRAFICO
		if ($("#informes").val() == 'sem_resum_grafico') { 
			if ((mes<6 && anio4dint==2014) || anio4dint<2014) {
				mostrarVentana=false;
				alert('No existen Informes de Resumen Grafico para la fecha seleccionada');
			}
			direccion02 = carpeta_pdfs + '/resumen_grafico/' + anio + '/';
			direccion02 += semana + '_RESUMEN_GRAFICO_' + fecha_ultimo_domingo + '.pdf'; 
		}

		//console.log(direccion02);

		
		// ********************************************
		//                              _        
		//  _ __  ___ _ _  ____  _ __ _| |___ ___
		// | '  \/ -_) ' \(_-< || / _` | / -_|_-<
		// |_|_|_\___|_||_/__/\_,_\__,_|_\___/__/
		// ********************************************

		if ($("#informes").val() == 'mes_spot_promedio' || $("#informes").val() == 'mes_postdespacho'        || $("#informes").val() == 'mes_listaagentes' || 
                    $("#informes").val() == 'mes_ite'           || $("#informes").val() == 'mes_dterindicativo_indi' || 
                    $("#informes").val() == 'mes_dter'          || $("#informes").val() == 'mes_plp' || $("#informes").val() == 'mes_ageninhab' ) {
			
			// problema arreglado 03022016 AGS
			// pòr ajustes y validaciones en los anteriores reportes se ajusta el año cosa que no debe pasar con esos reportes
			if (anio4dint>=2016) { 
				//anio='2016';
				anio=''+anio4dint;
			} 
		
			if ($("#informes").val() == 'mes_spot_promedio') { direccion02 = carpeta_pdfs + '/' + anio + '/spot/GPSP' + anio + mes + '01_01.htm'; }
			if ($("#informes").val() == 'mes_postdespacho') { 
				botonindice=1;
				if ((mesint<7 && anio4dint==2007) || anio4dint<=2006) {
					mostrarVentana=false;
					alert('No existen Informes Mensuales de Postdespacho para la fecha seleccionada');
				} else if (mesint>=1 && anio4dint>=2013) {
					botonindice=0;
					direccion02 = carpeta_pdfs + '/post_despacho/POSDESPACHO_MENSUAL/'+ anio + '/IPM' + anio + mes + '.zip'; 
				} else
					direccion02 = carpeta_pdfs + '/' + anio + '/posdespachomensual/' + mes_txt + '/IPM' + anio + mes + '01_01.pdf'; 
			}

			if ($("#informes").val() == 'mes_listaagentes') { 
				if (anio4dint < 2019 || (mesint < 9 && anio4dint == 2019)) {
					mostrarVentana=false;
					alert('No existe la Lista de Agentes Habilitados para la fecha seleccionada');
				} else {
 					direccion02 = carpeta_pdfs + '/ListaAgentes/Agentes_Habilitados_' + mes + anio + '.pdf'; 
				}                                
			}
			
			// Solicitado por Jose Luis Molina 20211222
			if ($("#informes").val() == 'mes_ageninhab') { 
				if (anio4dint < 2021 || (mesint < 12 && anio4dint == 2021)) {
					mostrarVentana=false;
					alert('No existe la Lista de Agentes y Grandes Usuarios Inhabilitados para la fecha seleccionada');
				} else {
 					direccion02 = carpeta_pdfs + '/AgentesInhabilitados/' + anio + '/Agentes_Inhabilitados_' + anio + mes + '.pdf'; 
				}                                
			}

			//--------------------------------
			// ----- I T E -----
			if ($("#informes").val() == 'mes_ite') { 
				if (anio4dint<2000) {
					mostrarVentana=false;
					alert('No existen Informes de Transacciones Economicas para la fecha seleccionada');
				} else if (anio4dint>=2000 && anio4dint<=2002) {
					//botonindice=1;
					//direccion02 = carpeta_pdfs + '/' + anio + '/InfTraneco/ITE'+ anio + mes + '01_01.pdf';
					direccion02 = '/'+carpeta_padre+'ite.php?fecha=Inf'+mes+anio+'&anio=' + anio;
				} else if (anio4dint>=2013 && mesint>5) {
					direccion02 = '/'+carpeta_padre+'ite.php?fecha='+mes+'-'+anio+'&anio=' + anio;
				} else if (anio4dint>=2014) {
					direccion02 = '/'+carpeta_padre+'ite.php?fecha='+mes+'-'+anio+'&anio=' + anio;
				} else if (anio4dint==2004 && mesint==9) {
					direccion02 = '/'+carpeta_padre+'ite.php?fecha='+mes+'-'+anio+'&anio=' + anio;
				} else { 
					direccion02 = carpeta_pdfs + '/' + anio + '/InfTraneco/ITE'+ anio + mes + '01_01.pdf';
				}
	
			}
			
			if ($("#informes").val() == 'mes_dterindicativo_indi') { 
				if (anio4dint<2013) {
					mostrarVentana=false;
					alert('No existen DTER Indicativo para la fecha seleccionada');
				}
				// mes_largo mesint
				var cadenames=mes_largo[mesint].substring(0,1)+mes_largo[mesint].substring(1).toLowerCase();
				direccion02 = carpeta_pdfs + '/programas_interconexion/DTER_RMER_PDC/' + anio + '/DTER_indicativo_RMER_PDC_' + cadenames +'_'+ anio + '.pdf'; 
			}
			
			if ($("#informes").val() == 'mes_dter') {
				var nompredter='DTER_oficial_RMER_PDC_';
				if (anio4dint<2013) {
					mostrarVentana=false;
					alert('No existen DTER para la fecha seleccionada');
				} else if (anio4dint>=2019) { // modificacion solicitada por Omar Maldonado. 13/Feb/2019 Alexander Godinez
					nompredter='DTER_oficial_RMER_';
				}
				// mes_largo mesint
				var cadenames=mes_largo[mesint].substring(0,1)+mes_largo[mesint].substring(1).toLowerCase();
				direccion02 = carpeta_pdfs + '/publicaciones_mer_definitivo/DTER_RMER_PDC/' + anio + '/' + nompredter + cadenames +'_'+ anio + '.pdf'; 
			}
			
			// PLP MENSUAL
			if ($("#informes").val() == 'mes_plp') { 
				if (anio4dint<2017) {
					mostrarVentana=false;
					alert('No existen archivos para la fecha seleccionada');
				}
				// mes_largo mesint
				var cadenames=mes_largo[mesint].substring(0,1)+mes_largo[mesint].substring(1).toLowerCase();
				//direccion02 = carpeta_pdfs + '/programacion_mensual/MENSUAL/' + anio + '/' + mes + 'EDM' + anio + '.xls';
				direccion02 = '/'+carpeta_padre + 'progmen.php?a=' + anio + '&m=' + mes; 
			}
		}
		
		// ********************************************
		//  _       _                             _ 
		// | |_ _ _(_)_ __  ___ _ _  ____  _ __ _| |
		// |  _| '_| | '  \/ -_) ' \(_-< || / _` | |
		//  \__|_| |_|_|_|_\___|_||_/__/\_,_\__,_|_|
		// ********************************************

		if ($("#informes").val() == 'trimes_programacion' ) {
			
			// problema arreglado 03022016 AGS
			// pòr ajustes y validaciones en los anteriores reportes se ajusta el año cosa que no debe pasar con esos reportes
			if (anio4dint>=2016) { 
				//anio='2016';
				anio=''+anio4dint;
			} 
			
			// TRIMENSUAL
			if ($("#informes").val() == 'trimes_programacion') { 
				if (anio4dint<2021) {
					mostrarVentana=false;
					alert('No existen archivos para la fecha seleccionada');
				}
				// mes_largo mesint
				var cadenames=mes_largo[mesint].substring(0,1)+mes_largo[mesint].substring(1).toLowerCase();
				direccion02 = '/'+carpeta_padre + 'progtrimen.php?a=' + anio + '&m=' + mes; 
			}
		}

		if (anio4dint>=2016) { 
			//anio='2016'
			anio=''+anio4dint;
		}
		
		//+------------------------------------------+
		//|             Informes Anuales             |
		//+------------------------------------------+
		if ($("#informes").val() == 'ano_spot_anual') { 
			if (anio4dint<2004) {
				mostrarVentana=false;
				alert('No existen Informes de Precio SPOT para la fecha seleccionada');
			}
			direccion02 = carpeta_pdfs + '/' + anio + '/spot/PSA' + anio + '0101.xls'; 
		}

		if ($("#informes").val() == 'ano_despacho_estacional') { 
			if (anio4dint>=2012) {
				var aniosig_txt = '' + (anio4dint + 1);
				//direccion02 = carpeta_pdfs + '/programas_despacho/03_PROGRAMAS_DE_LARGO_PLAZO/' + anio + '-' + aniosig_txt + '/01_PLP'+ anio + '0501_VP.pdf'; 
				direccion02 = '/'+carpeta_padre+'plp.php?anio=' + anio;
			} else
				direccion02 = carpeta_pdfs + '/' + anio + '/despacho/PLP'+ anio + '0101.pdf'; 
		}

		//if ($("#informes").val() == 'ano_medicion') { direccion02 = 'INFO_ADG_12_2010_2_.pdf'; } // Revisar si existe para mas aos
		//if ($("#informes").val() == 'ano_generacion_pdf')     { direccion02 = carpeta_pdfs + '/' + anio + '/generacion/Generacion_' + anio + '_WEB.pdf'; }
		//if ($("#informes").val() == 'ano_generacion_xls') { direccion02 = carpeta_pdfs + '/' + anio + '/generacion/Generacion_' + anio + '_WEB.xls'; }
		if ($("#informes").val() == 'ano_generacion_pdf') { 
			if (anio4dint<2006) {
				mostrarVentana=false;
				alert('No existen Informes de Generacion Mensual para la fecha seleccionada');
			}
			//direccion02 = carpeta_pdfs + '/' + anio + '/generacion/GM' + anio + '0101.pdf'; //debido a la notificacion automatica 20191217 AGS
			direccion02 = carpeta_pdfs + '/pub_gen_mensual_x_planta/GM' + anio + '0101.pdf'; 
		}
		if ($("#informes").val() == 'ano_generacion_xls') { 
			if (anio4dint<2006) {
				mostrarVentana=false;
				alert('No existen Informes de Generacion Mensual para la fecha seleccionada');
			}
			//direccion02 = carpeta_pdfs + '/' + anio + '/generacion/GM' + anio + '0101.xls'; //debido a la notificacion automatica 20191217 AGS
			direccion02 = carpeta_pdfs + '/pub_gen_mensual_x_planta/GM' + anio + '0101.';
			if (anio4dint<2021) {
				direccion02 += 'xls';
			} else {
				direccion02 += 'xlsx';
			}
		}
		
		
		//if ($("#informes").val() == 'ano_estadistico_anual') { direccion02 = carpeta_pdfs + '/informes/' + anio + '/INFEST' + anio + '0101_01.pdf'; }
		if ($("#informes").val() == 'ano_estadistico_anual') {
			if (anio>=2013) {
				direccion02 = carpeta_padre + 'informe_estadistico.php?anio=' + anio + '&fecha=' + anio + '0101';
			} else
				direccion02 = carpeta_pdfs + '/informes/' + anio + '/INFEST' + anio + '0101_01.pdf';
			
		}
		
		if ($("#informes").val() == 'ano_memoria_labores') { 
			//if (anio4dint<2003) {
			//	mostrarVentana=false;
			//	alert('No existen Informes de Memoria de Labores para la fecha seleccionada');
			//}
			direccion02 = carpeta_pdfs + '/memorias_labores/MEMLAB' + anio + '0101_1.pdf'; 
		}
		// agregados
		if ($("#informes").val() == 'ano_demanda_firme') {
			//direccion02 = carpeta_pdfs + '/' + anio + '/DFC' + anio + '.pdf';
			direccion02 = '/dfc.php?anio=' + anio;
		}
		
		if ($("#informes").val() == 'ano_oferta_firme') { direccion02 = carpeta_pdfs + '/' + anio + '/OFE' + anio + '.pdf'; }

		
		if ($("#informes").val() == 'ano_cap_inst') { direccion02 = carpeta_pdfs + '/' + anio +'/Capacidad_Instalada_' + anio + '.xls'; }
		
		//   ___        __                                      _      _   __  __ _____ ____  
		//  |_ _|_ __  / _| ___  _ __ _ __ ___   ___  ___    __| | ___| | |  \/  | ____|  _ \ 
		//   | || '_ \| |_ / _ \| '__| '_ ` _ \ / _ \/ __|  / _` |/ _ \ | | |\/| |  _| | |_) |
		//   | || | | |  _| (_) | |  | | | | | |  __/\__ \ | (_| |  __/ | | |  | | |___|  _ < 
		//  |___|_| |_|_|  \___/|_|  |_| |_| |_|\___||___/  \__,_|\___|_| |_|  |_|_____|_| \_\
		
		if ($("#informes").val() == 'desdiario_mer_indi') { 
			botonindice=1; 
			
			if ((mesint<4 && anio4dint==2013) || anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Despacho RMER para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'pd_rmer_indi.php?fecha='+dia+mes+anio+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		if ($("#informes").val() == 'desdiario_mer') { 
			botonindice=1; 
			
			if ((mesint<4 && anio4dint==2013) || anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Despacho RMER para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'pd_rmer.php?fecha='+dia+mes+anio+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		// CONCILIACION DIARIA PROGRAMADA
		if ($("#informes").val() == 'cdiariaprog_indi') { 
			botonindice=0; 
			
			if (anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Conciliacion Diaria Programada para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/2012/cddiaria_prog_indi.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		if ($("#informes").val() == 'cdiariaprog') { 
			botonindice=0; 
			
			if (anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Conciliacion Diaria Programada para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'cddiaria_prog.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		// CONCILIACION DIARIA EN TIEMPO REAL
		if ($("#informes").val() == 'cdiariatiemporeal_indi') { 
			botonindice=0; 
			
			if (anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Conciliacion Diaria En tiempo Real para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'cddiaria_real_indi.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		if ($("#informes").val() == 'cdiariatiemporeal') { 
			botonindice=0; 
			
			if (anio4dint<2013) {
				mostrarVentana=false;
				alert('No existen Informes de Conciliacion Diaria En tiempo Real para la fecha seleccionada');
			} else if (anio4dint>=2013) {
				botonindice=0; 
				//direccion02 = carpeta_pdfs + '/programas_despacho/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + anio + '/01_PROGRAMAS_DE_DESPACHO_DIARIO/' + mes + '_' + mes_largo[mesint] + '/WEB' + dia + mes + anio + extension;
				direccion02 = '/'+carpeta_padre+'cddiaria_real.php?fecha='+anio+mes+dia+'&mes='+mesint+'&anio=' + anio;
			} 
		}
		
		//-----------------------------------------------------------------------------------------------
		//centered_free_window(direccion01 + direccion02, 900, 400, 'true', 'display01');
		if ($("#informes").val() != 'XXX') { 
			if (mostrarVentana) {
				var docu = direccion01 + direccion02;
				if( docu != "https://www.amm.org.gt/"){
				if (botonindice==0){
					var docurl = direccion01 + direccion02;
				//	$("#docs-view").attr("src", docurl);
					//alert((docurl.charAt(docurl.length-1)));
					//var textopdf = (docurl.charAt(docurl.length-1));
					var txtfinal = (docurl.substr(-3));
					var txtsp = docurl.indexOf("sharepoint");
					
					if ( txtfinal == "pdf" || txtsp > 0){
						window.open(docurl, '_blank');
					}else{
						$("#docs-view").attr("src", docurl);
					} 
				}
				else if (botonindice==1){
				var docurl = direccion01 + direccion02;
				//	$("#docs-view").attr("src", docurl);
					//alert((docurl.charAt(docurl.length-1)));
					var txtfinal = (docurl.substr(-3));
					var txtsp = docurl.indexOf("sharepoint");
					
					if ( txtfinal == "pdf" || txtsp > 0){
						window.open(docurl, '_blank');
					}else{
						$("#docs-view").attr("src", docurl);
					} 
				}
			}
			}
		}
	}
}

// funcion que verifica la fecha seleccionada no sea mayor a hoy, agregada por Alex Godinez
function verificaFecha(fecSeleccionada){
	
	var fec1=new Date();
	if (fecSeleccionada>fec1) {
		alert('La fecha seleccionada es mayor al dia de hoy, tiene que seleccionar una menor. Intente de nuevo.');
		return false;
	} else {
		return true;
	}
	
}

function ultimoDomingo(d) {
  var day = d.getDay(),
      diff = d.getDate() - day;
  return new Date(d.setDate(diff));
}


$(function(){
	$('#calendario').datepicker({
		inline: true,
		altField: "#fecha_seleccionada",
		altFormat: "dd/mm/yy",
		showOtherMonths: true,
		selectOtherMonths: true,
		changeMonth: true,
		changeYear: true,
		maxDate: "+1d", //AGS +0y
		minDate: new Date(1998, 1-1, 1) //AGS
	});
});

/*$(function() {
		var fecha = new Date();
		var anio = fecha.getFullYear();
		// para mostrar el calendario mensual
		$('#cal_mensual').monthpicker({
			StartYear: 2003,
			finalYear: anio,
			monthNames: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
		});
	});*/



$(function() {
	$( "input:submit, a, button", ".demo" ).button();
	$( "a", ".demo" ).click(function() { return false; });
});
