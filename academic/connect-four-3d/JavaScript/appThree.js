import { play, resetGame } from './logica.js';
import * as THREE from 'three';
import { OrbitControls } from 'OrbitControls';
import { GLTFLoader } from 'GLTFLoader';
import {EXRLoader} from 'EXRLoader';

//configuração inicial da cena
const scene = new THREE.Scene();
scene.background = new THREE.Color("lightblue"); 
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

//-----------------------------------------------------------------------------------------------------

// Criar popup e elementos de overlay
const overlay = document.createElement('div');
overlay.id = 'overlay';
overlay.style.display = 'none';
overlay.style.position = 'fixed';
overlay.style.top = '0';
overlay.style.left = '0';
overlay.style.width = '100%';
overlay.style.height = '100%';
overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
overlay.style.zIndex = '999';

const winnerPopup = document.createElement('div');
winnerPopup.id = 'winner-popup';
winnerPopup.style.display = 'none';
winnerPopup.style.position = 'fixed';
winnerPopup.style.top = '50%';
winnerPopup.style.left = '50%';
winnerPopup.style.transform = 'translate(-50%, -50%)';
winnerPopup.style.padding = '20px';
winnerPopup.style.backgroundColor = 'white';
winnerPopup.style.border = '2px solid black';
winnerPopup.style.zIndex = '1000';

const winnerMessage = document.createElement('p');
winnerMessage.id = 'winner-message';

const homeButton = document.createElement('button');
homeButton.innerText = 'Home';
homeButton.onclick = () => window.location.href = 'index.html'; // Navegar para index.html

const resetButton = document.createElement('button');
resetButton.innerText = 'Reset';
resetButton.onclick = closePopup; // Fechar popup e reiniciar o jogo

winnerPopup.appendChild(winnerMessage);
winnerPopup.appendChild(homeButton);
winnerPopup.appendChild(resetButton);
document.body.appendChild(overlay);
document.body.appendChild(winnerPopup);

// Função para mostrar o popup
window.showPopup = function (message) {
    winnerMessage.innerText = message;
    overlay.style.display = 'block';
    winnerPopup.style.display = 'block';
};

//----------------------------------------------------------------------------------------------------------------------

// Carregar Texturas
const textureLoader = new THREE.TextureLoader();
const grassTexture = textureLoader.load('../textures/grass_texture.jpg');

// Adicionar plano de relva no chão
const planeGeometry = new THREE.PlaneGeometry(2000, 1000);
const planeMaterial = new THREE.MeshBasicMaterial({ map: grassTexture });
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
plane.rotation.x = -Math.PI / 2;
plane.position.y = 12; // Ajuste a altura do chão conforme necessário
scene.add(plane);


// Carregar textura EXR para o céu
const exrLoader = new EXRLoader();
exrLoader.load('../textures/sunflowers_puresky_4k.exr', function(texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.background = texture;
});

//------------------------------------------------------------------------------------------------------------------------------

//load do modelo da casa
const loader = new GLTFLoader();
loader.load('casa_model/scene.gltf', function(gltf) {
    scene.add(gltf.scene);
    gltf.scene.scale.set(16, 16, 16);
    gltf.scene.position.set(0, 0, 0); 
});

//teto da casa

const housePosition = new THREE.Vector3(15, 0, 23);
const wallHeight = 87; // Altura das paredes

const roofGeometry = new THREE.BoxGeometry(160, 10, 220);
const roofMaterial = new THREE.MeshStandardMaterial({ color: 0xD2B48C, side: THREE.DoubleSide }); // Marrom e visível dos dois lados

// Criar a malha do teto 
const roof = new THREE.Mesh(roofGeometry, roofMaterial);
roof.position.set(housePosition.x, housePosition.y + wallHeight, housePosition.z); // Posicionar no topo das paredes

// Adicionar o teto à cena
scene.add(roof);

//porta da casa
const doorGeometry = new THREE.BoxGeometry(55, 2, 25);
const doorMaterial = new THREE.MeshStandardMaterial({ color: 0x8B4513, side: THREE.DoubleSide }); // Marrom e visível dos dois lados

// Criar a malha da porta
const door = new THREE.Mesh(doorGeometry, doorMaterial);
door.position.set(-56.6, 40, -58.2); 
door.rotation.x = Math.PI / 2;
door.rotation.y = Math.PI / 2;

// Adicionar a porta à cena
scene.add(door);

// maçaneta da porta (lado de dentro)
const inside_knobGeometry = new THREE.SphereGeometry(1, 32, 32); // Ajuste o raio e a segmentação conforme necessário

const inside_knobMaterial = new THREE.MeshStandardMaterial({ color: 0xCCCCCC }); // Ajuste a cor conforme necessário

const inside_knob = new THREE.Mesh(inside_knobGeometry, inside_knobMaterial);

// Posicionar a maçaneta na porta
inside_knob.position.set(-66.6, 40, -57.2); // Ajuste as coordenadas conforme necessário

// Adicionar a maçaneta à cena
scene.add(inside_knob);

// maçaneta da porta (lado de fora)
const outside_knobGeometry = new THREE.SphereGeometry(1, 32, 32); // Ajuste o raio e a segmentação conforme necessário

const outside_knobMaterial = new THREE.MeshStandardMaterial({ color: 0xCCCCCC }); // Ajuste a cor conforme necessário

const outside_knob = new THREE.Mesh(outside_knobGeometry, outside_knobMaterial);

// Posicionar a maçaneta na porta
outside_knob.position.set(-66.6, 40, -59.2); // Ajuste as coordenadas conforme necessário

// Adicionar a maçaneta à cena
scene.add(outside_knob);
//----------------------------------------------------------------------------------------------------------------------

//Camera em perspetiva e ortografica

// Definição das câmaras
const perspectiveCamera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const orthographicCamera = new THREE.OrthographicCamera(
    window.innerWidth / -20, window.innerWidth / 20, window.innerHeight / 20, window.innerHeight / -20, 0.1, 1000
);

let currentCamera = perspectiveCamera;

//------------------------------------------------------------------------------------------------------------------

// Posicionamento e visualização da câmera inicial

let currentPlayer = 1; // Inicializa com o jogador 1
const boardPosition = new THREE.Vector3(-7.5, 40, 16);
const cameraDistance = 40; // Distância desejada da câmera ao tabuleiro

// Posicionamento e visualização da câmera inicial
const initialCameraPosition = new THREE.Vector3(-7.5, 45, 40); // Use os valores iniciais que você deseja
const initialCameraZoom = 2.2; // Valor inicial de zoom para a câmera ortográfica

function setInitialCameraPosition() {
    perspectiveCamera.position.copy(initialCameraPosition);
    perspectiveCamera.lookAt(boardPosition);
    perspectiveCamera.updateProjectionMatrix();

    orthographicCamera.position.copy(initialCameraPosition);
    orthographicCamera.lookAt(boardPosition);
    orthographicCamera.zoom = initialCameraZoom;
    orthographicCamera.updateProjectionMatrix();
}

setInitialCameraPosition();

//----------------------------------------------------------------------------------------------------------------------

// Função para configurar os controles de órbita com restrições
function setupControls(camera) {
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;
    controls.target.set(boardPosition.x, boardPosition.y, boardPosition.z);

    // Limites de zoom e movimento para a câmera de perspectiva
    if (camera instanceof THREE.PerspectiveCamera) {
        controls.minDistance = 10; // Distância mínima do zoom (ajuste conforme necessário)
        controls.maxDistance = 200; // Distância máxima do zoom (ajuste conforme necessário)
    }

    // Limites de zoom e movimento para a câmera ortográfica
    if (camera instanceof THREE.OrthographicCamera) {
        controls.minZoom = 1.8; // Zoom mínimo (ajuste conforme necessário)
        controls.maxZoom = 4; // Zoom máximo (ajuste conforme necessário)
        camera.zoom = THREE.MathUtils.clamp(camera.zoom, controls.minZoom, controls.maxZoom);
        camera.updateProjectionMatrix();
    }

    // Limitar a movimentação para que o usuário não possa ir para debaixo do chão
    controls.maxPolarAngle = Math.PI / 2; // Limite o ângulo polar para que a câmera não possa ir abaixo do horizonte

    controls.update();
    return controls;
}

// Inicialização dos controles para a câmera atual
let controls = setupControls(currentCamera);


//----------------------------------------------------------------------------------------------------------------------

//alternar cameras

// Função para alternar entre câmaras
function toggleCamera() {
    if (currentCamera === perspectiveCamera) {
        currentCamera = orthographicCamera;
        orthographicCamera.position.copy(perspectiveCamera.position);
        orthographicCamera.rotation.copy(perspectiveCamera.rotation);
        orthographicCamera.zoom = THREE.MathUtils.clamp(orthographicCamera.zoom, 1.8, 4); // Ajuste conforme necessário
        orthographicCamera.updateProjectionMatrix();
    } else {
        currentCamera = perspectiveCamera;
        perspectiveCamera.position.copy(orthographicCamera.position);
        perspectiveCamera.rotation.copy(orthographicCamera.rotation);
        perspectiveCamera.updateProjectionMatrix();
    }
    controls.dispose(); // Remove os antigos controlos
    controls = setupControls(currentCamera); // Cria novos controlos para a câmera atual
}

// Evento para alternar câmaras quando o botão for clicado
document.getElementById('toggleCameraButton').addEventListener('click', toggleCamera);


// Função para resetar a câmera para a posição e orientação iniciais
function resetCamera() {
    setInitialCameraPosition();
    controls.target.set(boardPosition.x, boardPosition.y, boardPosition.z);
    controls.update();
}

// Evento para resetar a câmera quando o botão for clicado
document.getElementById('resetCameraButton').addEventListener('click', resetCamera);

// redimensionamento de troca de camara
window.addEventListener('resize', () => {
    perspectiveCamera.aspect = window.innerWidth / window.innerHeight;
    perspectiveCamera.updateProjectionMatrix();

    orthographicCamera.left = window.innerWidth / -20;
    orthographicCamera.right = window.innerWidth / 20;
    orthographicCamera.top = window.innerHeight / 20;
    orthographicCamera.bottom = window.innerHeight / -20;
    orthographicCamera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);
});


// Renderização com a câmara atual
function animateCamera() {
    requestAnimationFrame(animateCamera);
    controls.update();
    renderer.render(scene, currentCamera);
}

animateCamera();

//---------------------------------------------------------------------------------------------------------------------------

//animacao de troca de jogador
function updateCameraPosition(targetAngle) {
    const duration = 2000; // Duração da animação em milissegundos
    const startTime = performance.now();
    const radius = 24; // Distância desejada da câmera ao tabuleiro
    
    const startAngle = Math.atan2(currentCamera.position.z - boardPosition.z, currentCamera.position.x - boardPosition.x);

    function animate() {
        const elapsedTime = performance.now() - startTime;
        const t = Math.min(elapsedTime / duration, 1); // Progresso da animação (de 0 a 1)
        const currentAngle = startAngle + (targetAngle - startAngle) * t;

        // Atualiza a posição da câmera usando interpolação angular
        currentCamera.position.x = boardPosition.x + radius * Math.cos(currentAngle);
        currentCamera.position.z = boardPosition.z + radius * Math.sin(currentAngle);
        currentCamera.position.y = boardPosition.y + 5;

        currentCamera.lookAt(boardPosition); // Manter a câmera olhando para o tabuleiro

        if (t < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

function triggerCameraUpdate() {
    let targetAngle;

    if (currentPlayer === 1) {
        targetAngle = Math.PI / 2; // Ângulo para o jogador 1 (90 graus)
    } else {
        targetAngle = -Math.PI / 2; // Ângulo para o jogador 2 (-90 graus)
    }

    updateCameraPosition(targetAngle);
}

// ----------------------------------------------------------------------------------------------------------------------------------

// Configuração do tabuleiro
const boardRows = 6;
const boardCols = 7;
const board = [];
for (let i = 0; i < boardCols; i++) {
    board[i] = new Array(boardRows).fill(null);
}

// Raycaster para detectar cliques do mouse
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

let ghostPiece;
function createGhostPiece() {
    const ghostPieceGeometry = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 32);
    const ghostPieceMaterial = new THREE.MeshLambertMaterial({ color: currentPlayer === 1 ? 'yellow' : 'red', side: THREE.DoubleSide, opacity: 0.5, transparent: true });
    ghostPiece = new THREE.Mesh(ghostPieceGeometry, ghostPieceMaterial);
    ghostPiece.rotation.x = Math.PI / 2;
    scene.add(ghostPiece);
}

function createBoard() {
    // Criação do tabuleiro como um plano
    const boardGroup = new THREE.Group();
    const boardGeometry = new THREE.BoxGeometry(8.5, 7.5, 0.5);
    const boardMaterial = new THREE.MeshLambertMaterial({ color: 'blue', side: THREE.DoubleSide, transparent: true });
    const boardMesh = new THREE.Mesh(boardGeometry, boardMaterial);
    boardMesh.position.set(0,0,0);
    boardGroup.add(boardMesh);

    // Base do tabuleiro
    const baseGeometry = new THREE.BoxGeometry(9, 1, 5);
    const baseMaterial = new THREE.MeshLambertMaterial({ color:'blue'});
    const baseMesh = new THREE.Mesh(baseGeometry, baseMaterial);
    baseMesh.position.set(0, -4, 0);
    boardGroup.add(baseMesh);

    //buracos do tabuleiro
    const xOffset = 0 - (7 * 1.1) / 2 + 0.55;
    const yOffset = (6 * 1.1) / 2 - 0.55;

    for (let row = 0; row < boardRows; row++) {
        for (let col = 0; col < boardCols; col++) {
            const holeGeometry = new THREE.CylinderGeometry(0.5, 0.5, 0.51, 32);
            const holeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0});
            const holeMesh = new THREE.Mesh(holeGeometry, holeMaterial);
            holeMesh.position.x = col * 1.1 + xOffset;
            holeMesh.position.y = row * 1.1 - yOffset;
            holeMesh.position.z = 0;
            holeMesh.rotation.x = Math.PI / 2;
            boardGroup.add(holeMesh);
        }
    }
    boardGroup.position.set(boardPosition.x, boardPosition.y, boardPosition.z);
    
    scene.add(boardGroup);

    // Criação da fissura no topo do tabuleiro
    const fissuraGeometry = new THREE.BoxGeometry(8, 0.31, 0.3);
    const fissuraMaterial = new THREE.MeshLambertMaterial({ color: 0x000000, transparent: true, opacity: 0.35 });
    const fissuraMesh = new THREE.Mesh(fissuraGeometry, fissuraMaterial);
    fissuraMesh.position.set(boardPosition.x, boardPosition.y + 3.6, boardPosition.z); // Ajustar a posição para ficar no topo do tabuleiro
    scene.add(fissuraMesh);

    return boardGroup;
}

const boardMesh = createBoard();

createGhostPiece();

function animatePiece(piece, targetY) {
    function animate() {
        if (piece.position.y > targetY) {
            piece.position.y -= 0.3;
            requestAnimationFrame(animate);
        } else {
            piece.position.y = targetY;
        }
    }
    animate();
}

//----------------------------------------------------------------------------------------------------------------------------------------------------

function Play(column) {
    const xOffset = (column * 1.1) + boardPosition.x - ((boardCols - 1) * 1.1) / 2;
    const initialY = boardPosition.y + 5; // Posição inicial acima do tabuleiro
    const zPosition = boardPosition.z;

    for (let row = 0; row < boardRows; row++) {
        if (board[column][row] === null) {
            const pieceGeometry = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 32);
            let pieceMaterial;
            if (currentPlayer === 1) {
                pieceMaterial = new THREE.MeshLambertMaterial({ color: 'yellow', side: THREE.DoubleSide });
            } else if (currentPlayer === 2) {
                pieceMaterial = new THREE.MeshLambertMaterial({ color: 'red', side: THREE.DoubleSide });
            }
            const piece = new THREE.Mesh(pieceGeometry, pieceMaterial);
            piece.position.set(xOffset, initialY, zPosition); // Posição inicial acima do tabuleiro
            piece.rotation.x = Math.PI / 2;
            scene.add(piece);
            board[column][row] = currentPlayer;

            play(column); // Chama a função play do logica.js

            const targetY = boardPosition.y + (row * 1.1) - ((boardRows - 1) * 1.1) / 2;
            animatePiece(piece, targetY);

            currentPlayer = currentPlayer === 1 ? 2 : 1; // Alternar jogador
            triggerCameraUpdate();
            scene.remove(ghostPiece);
            createGhostPiece();
            break;
        }
    }
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, currentCamera);
}

animate();

window.addEventListener('resize', () => {
    currentCamera.aspect = window.innerWidth / window.innerHeight;
    currentCamera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

//-------------------------------------------------------------------------------------------------------------------
// Função para mover a peça fantasma
function onMouseMove(event) {
    if (overlay.style.display === 'block') {
        return;
    }

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, currentCamera);

    const intersects = raycaster.intersectObject(boardMesh);

    if (intersects.length > 0) {
        const intersect = intersects[0];
        const x = intersect.point.x - boardMesh.position.x;
        const col = Math.floor((x + (7 * 1.1) / 2) / 1.1);
        if (col >= 0 && col < boardCols) {
            const xOffset = (col * 1.1) + boardPosition.x - ((boardCols - 1) * 1.1) / 2;
            ghostPiece.position.set(xOffset, 4.5 + boardPosition.y, boardPosition.z);
        }
    }
}

// Atualize a função onMouseClick para verificar se o popup está visível
function onMouseClick(event) {
    if (overlay.style.display === 'block') {
        return;
    }

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, currentCamera);

    const intersects = raycaster.intersectObject(boardMesh);

    if (intersects.length > 0) {
        const intersect = intersects[0];
        const x = intersect.point.x - boardMesh.position.x;
        const col = Math.floor((x + (7 * 1.1) / 2) / 1.1);
        if (col >= 0 && col < boardCols) {
            Play(col);
        }
    }
}

window.addEventListener('mousemove', onMouseMove);
window.addEventListener('click', onMouseClick);

//---------------------------------------------------------------------------------------------------------------------------------------------------

// Criar as luzes

const pointLight = new THREE.PointLight('red', 2000, 100); // luz vermelha
pointLight.position.set(-7.5, 40, 16);
scene.add(pointLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 2); // luz semelhante à do sol
directionalLight.position.set(10, 20, 10);
directionalLight.castShadow = true; // Para sombras mais realistas
scene.add(directionalLight);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.5); // luz ambiente branca suave
scene.add(ambientLight);

// Funções para ligar/desligar luzes
function toggleLight(light) {
    light.visible = !light.visible;
}


// Função para rotacionar a luz direcional ao redor da cena
function rotateDirectionalLight(angle) {
    const newPositionX = Math.sin(angle) * 10;
    const newPositionZ = Math.cos(angle) * 10;
    directionalLight.position.set(newPositionX, directionalLight.position.y, newPositionZ);
    directionalLight.target.position.set(0, 0, 0);
}

// Função para mover a luz direcional verticalmente
function moveDirectionalLightVertical(position) {
    // Verifica se a posição está dentro do intervalo desejado
    if (position >= -180 && position <= 180) {
        directionalLight.position.y = position;
    } else {
        console.error("A posição vertical deve estar entre -180 e 180.");
    }
}

// Evento para alternar luzes quando os botões forem clicados
document.getElementById('togglePointLight').addEventListener('click', () => toggleLight(pointLight));
document.getElementById('toggleDirectionalLight').addEventListener('click', () => toggleLight(directionalLight));
document.getElementById('toggleAmbientLight').addEventListener('click', () => toggleLight(ambientLight));

const rotationSlider = document.getElementById('rotationSlider');
const verticalSlider = document.getElementById('verticalSlider');

rotationSlider.addEventListener('input', () => {
    const rotationValue = parseFloat(rotationSlider.value) * (Math.PI / 180);
    rotateDirectionalLight(rotationValue);
});

verticalSlider.addEventListener('input', () => {
    const verticalValue = parseFloat(verticalSlider.value);
    moveDirectionalLightVertical(verticalValue);
});

